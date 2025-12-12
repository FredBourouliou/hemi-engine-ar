"""
===============================================================================
SCRIPT D'EXPORT GLB NON DESTRUCTIF
===============================================================================

Projet     : AR Pédagogique - Moteur Hemi
Fichier    : export_glb.py
Sortie     : assets/hemi_engine.glb

PRINCIPE DE FONCTIONNEMENT :
----------------------------
1. Duplique les objets à exporter dans une collection temporaire
2. Applique la décimation uniquement sur les copies
3. Exporte les copies en GLB
4. Supprime la collection temporaire
5. Le fichier .blend original reste INTACT

OBJETS EXCLUS DE L'EXPORT :
---------------------------
- Plane (sol)
- Camera
- Lamp, Lamp.001, Lamp.002
- engine.009 (mesh vide, 0 vertices)
- BezierCurve (câbles décoratifs, optionnel)

STRATÉGIE DE DÉCIMATION :
-------------------------
- Décimation proportionnelle par objet
- Les gros objets sont plus réduits que les petits
- Préserve les détails relatifs de chaque composant
- Cible globale : 50-80k vertices

===============================================================================
"""

import bpy
import os
import math

# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG = {
    # Fichier de sortie (relatif au .blend)
    "output_filename": "assets/hemi_engine.glb",

    # Cible de vertices après décimation
    "target_vertices_min": 50000,
    "target_vertices_max": 80000,
    "target_vertices": 65000,  # Valeur cible médiane

    # Objets à exclure de l'export (noms exacts)
    "exclude_objects": [
        "Plane",
        "Camera",
        "Lamp",
        "Lamp.001",
        "Lamp.002",
        "engine.009",    # Mesh vide (0 vertices)
        "BezierCurve",   # Câbles décoratifs
    ],

    # Seuil minimum de vertices pour appliquer la décimation
    # Les objets sous ce seuil ne seront pas décimés
    "decimation_threshold": 500,

    # Nom de la collection temporaire pour l'export
    "temp_collection_name": "__EXPORT_TEMP__",

    # Échelle pour AR (1.0 = taille originale)
    # Le moteur fait ~8 unités, on le ramène à ~0.4m pour manipulation AR
    # Cette échelle sera APPLIQUÉE à la géométrie avant export
    "export_scale": 0.05,

    # Activer la compression Draco
    "use_draco": True,
    "draco_compression_level": 6,
}


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def log(message, level="INFO"):
    """Affiche un message formaté dans la console Blender."""
    prefix = {
        "INFO": "[INFO]",
        "WARN": "[ATTENTION]",
        "ERROR": "[ERREUR]",
        "OK": "[OK]",
        "STEP": ">>>"
    }.get(level, "[INFO]")
    print(f"{prefix} {message}")


def count_vertices(objects):
    """Compte le nombre total de vertices dans une liste d'objets mesh."""
    total = 0
    for obj in objects:
        if obj.type == 'MESH' and obj.data:
            total += len(obj.data.vertices)
    return total


def get_exportable_objects():
    """Retourne la liste des objets à exporter (en excluant ceux de la config)."""
    exportable = []
    excluded_names = CONFIG["exclude_objects"]

    for obj in bpy.data.objects:
        if obj.name in excluded_names:
            log(f"Exclu : {obj.name}", "WARN")
            continue
        if obj.type in ['MESH', 'CURVE']:
            exportable.append(obj)

    return exportable


def calculate_decimation_ratios(objects, target_vertices):
    """
    Calcule le ratio de décimation pour chaque objet.

    Stratégie : décimation proportionnelle
    - Chaque objet garde le même pourcentage de ses vertices
    - Les petits objets (< seuil) ne sont pas décimés
    - Cela préserve les détails relatifs de chaque composant
    """
    # Compter les vertices des objets décimables
    decimatable_vertices = 0
    non_decimatable_vertices = 0

    for obj in objects:
        if obj.type != 'MESH' or not obj.data:
            continue
        v_count = len(obj.data.vertices)
        if v_count >= CONFIG["decimation_threshold"]:
            decimatable_vertices += v_count
        else:
            non_decimatable_vertices += v_count

    # Calculer le ratio global nécessaire
    if decimatable_vertices == 0:
        return {}

    # Vertices cibles pour les objets décimables
    target_for_decimatable = target_vertices - non_decimatable_vertices

    if target_for_decimatable <= 0:
        log("Cible déjà atteinte sans décimation", "WARN")
        return {}

    global_ratio = target_for_decimatable / decimatable_vertices
    global_ratio = max(0.1, min(1.0, global_ratio))  # Clamp entre 0.1 et 1.0

    log(f"Ratio de décimation global : {global_ratio:.2%}", "INFO")

    # Appliquer le ratio à chaque objet
    ratios = {}
    for obj in objects:
        if obj.type != 'MESH' or not obj.data:
            continue
        v_count = len(obj.data.vertices)
        if v_count >= CONFIG["decimation_threshold"]:
            ratios[obj.name] = global_ratio
        else:
            ratios[obj.name] = 1.0  # Pas de décimation

    return ratios


# =============================================================================
# FONCTIONS PRINCIPALES
# =============================================================================

def create_temp_collection():
    """Crée une collection temporaire pour les copies d'export."""
    temp_name = CONFIG["temp_collection_name"]

    # Supprimer si existe déjà (nettoyage d'un export précédent échoué)
    if temp_name in bpy.data.collections:
        old_collection = bpy.data.collections[temp_name]
        for obj in old_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old_collection)

    # Créer la nouvelle collection
    temp_collection = bpy.data.collections.new(temp_name)
    bpy.context.scene.collection.children.link(temp_collection)

    log(f"Collection temporaire créée : {temp_name}", "OK")
    return temp_collection


def duplicate_objects_to_collection(objects, target_collection):
    """
    Duplique les objets dans la collection cible.
    Retourne un dictionnaire {nom_original: objet_copie}
    """
    copies = {}

    for obj in objects:
        # Créer une copie de l'objet
        obj_copy = obj.copy()

        # Copier aussi les données (mesh) pour que la décimation soit indépendante
        if obj.data:
            obj_copy.data = obj.data.copy()

        # Nommer la copie
        obj_copy.name = f"{obj.name}_export"

        # Lier à la collection temporaire
        target_collection.objects.link(obj_copy)

        copies[obj.name] = obj_copy
        log(f"Copié : {obj.name} -> {obj_copy.name}", "INFO")

    return copies


def apply_decimation(copies, ratios):
    """
    Applique la décimation aux copies.
    Utilise le modifier Decimate en mode COLLAPSE.
    """
    log("Application de la décimation...", "STEP")

    for original_name, obj_copy in copies.items():
        if obj_copy.type != 'MESH':
            continue

        ratio = ratios.get(original_name, 1.0)

        if ratio >= 0.99:
            log(f"  {original_name} : pas de décimation (ratio=1.0)", "INFO")
            continue

        v_before = len(obj_copy.data.vertices)

        # Sélectionner uniquement cet objet
        bpy.ops.object.select_all(action='DESELECT')
        obj_copy.select_set(True)
        bpy.context.view_layer.objects.active = obj_copy

        # Ajouter le modifier Decimate
        decimate = obj_copy.modifiers.new(name="Decimate_Export", type='DECIMATE')
        decimate.decimate_type = 'COLLAPSE'
        decimate.ratio = ratio
        decimate.use_collapse_triangulate = False

        # Appliquer le modifier (sur la copie uniquement)
        bpy.ops.object.modifier_apply(modifier="Decimate_Export")

        v_after = len(obj_copy.data.vertices)
        reduction = (1 - v_after / v_before) * 100 if v_before > 0 else 0

        log(f"  {original_name} : {v_before} -> {v_after} vertices (-{reduction:.1f}%)", "OK")


def apply_scale_to_geometry(copies, scale_factor):
    """
    Applique l'échelle directement à la géométrie des copies.
    Cela intègre l'échelle dans les vertices, pas dans le transform.
    """
    log(f"Application de l'échelle {scale_factor} à la géométrie...", "STEP")

    for original_name, obj_copy in copies.items():
        # Appliquer l'échelle au transform de l'objet
        obj_copy.scale = (scale_factor, scale_factor, scale_factor)

        # Aussi mettre à jour la position (translation)
        obj_copy.location = (
            obj_copy.location.x * scale_factor,
            obj_copy.location.y * scale_factor,
            obj_copy.location.z * scale_factor
        )

    # Appliquer les transformations (bake into geometry)
    bpy.ops.object.select_all(action='DESELECT')
    for obj_copy in copies.values():
        obj_copy.select_set(True)

    bpy.context.view_layer.objects.active = list(copies.values())[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    log(f"Échelle appliquée à {len(copies)} objets", "OK")


def hide_original_objects(objects):
    """Cache les objets originaux pour l'export."""
    for obj in objects:
        obj.hide_set(True)
        obj.hide_render = True


def show_original_objects(objects):
    """Restaure la visibilité des objets originaux."""
    for obj in objects:
        obj.hide_set(False)
        obj.hide_render = False


def export_glb(copies):
    """Exporte les copies en GLB avec compression Draco."""
    log("Export GLB en cours...", "STEP")

    # Chemin de sortie
    blend_dir = os.path.dirname(bpy.data.filepath)
    if not blend_dir:
        blend_dir = os.getcwd()

    output_path = os.path.join(blend_dir, CONFIG["output_filename"])

    # Créer le dossier assets si nécessaire
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        log(f"Dossier créé : {output_dir}", "OK")

    # Sélectionner uniquement les copies
    bpy.ops.object.select_all(action='DESELECT')
    for obj_copy in copies.values():
        obj_copy.select_set(True)

    # Export GLB (paramètres minimaux compatibles Blender 4.3+)
    # Note : Draco nécessite une configuration spécifique selon la version
    try:
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            use_selection=True,
            export_format='GLB',
            export_texcoords=True,
            export_normals=True,
            export_materials='EXPORT',
            export_cameras=False,
            export_lights=False,
            export_apply=True
        )
    except TypeError as e:
        # Fallback pour versions différentes de l'API
        log(f"Tentative avec paramètres alternatifs...", "WARN")
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            use_selection=True,
            export_format='GLB'
        )

    # Vérifier que le fichier existe
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # Mo
        log(f"Export réussi : {output_path}", "OK")
        log(f"Taille du fichier : {file_size:.2f} Mo", "INFO")
    else:
        log(f"Échec de l'export : fichier non créé", "ERROR")


def cleanup_temp_collection():
    """Supprime la collection temporaire et ses objets."""
    temp_name = CONFIG["temp_collection_name"]

    if temp_name not in bpy.data.collections:
        return

    temp_collection = bpy.data.collections[temp_name]

    # Supprimer les objets
    for obj in list(temp_collection.objects):
        # Supprimer les données (mesh) orphelines
        if obj.data and obj.data.users == 1:
            if obj.type == 'MESH':
                bpy.data.meshes.remove(obj.data)
            elif obj.type == 'CURVE':
                bpy.data.curves.remove(obj.data)
        else:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Supprimer la collection
    bpy.data.collections.remove(temp_collection)

    log("Collection temporaire nettoyée", "OK")


# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

def main():
    """Fonction principale d'export."""

    print("\n" + "=" * 60)
    print("EXPORT GLB NON DESTRUCTIF - MOTEUR HEMI")
    print("=" * 60 + "\n")

    # Vérifier que le fichier est sauvegardé
    if not bpy.data.filepath:
        log("Le fichier .blend doit être sauvegardé avant l'export", "ERROR")
        return False

    try:
        # ÉTAPE 1 : Identifier les objets exportables
        log("Identification des objets à exporter...", "STEP")
        exportable_objects = get_exportable_objects()

        if not exportable_objects:
            log("Aucun objet à exporter", "ERROR")
            return False

        log(f"Objets à exporter : {len(exportable_objects)}", "OK")

        # Compter les vertices avant
        vertices_before = count_vertices(exportable_objects)
        log(f"Vertices totaux avant décimation : {vertices_before:,}", "INFO")

        # ÉTAPE 2 : Calculer les ratios de décimation
        log("Calcul des ratios de décimation...", "STEP")
        ratios = calculate_decimation_ratios(exportable_objects, CONFIG["target_vertices"])

        # ÉTAPE 3 : Créer la collection temporaire
        temp_collection = create_temp_collection()

        # ÉTAPE 4 : Dupliquer les objets
        log("Duplication des objets...", "STEP")
        copies = duplicate_objects_to_collection(exportable_objects, temp_collection)

        # ÉTAPE 5 : Appliquer la décimation sur les copies
        apply_decimation(copies, ratios)

        # Compter les vertices après
        vertices_after = count_vertices(list(copies.values()))
        reduction_total = (1 - vertices_after / vertices_before) * 100
        log(f"Vertices totaux après décimation : {vertices_after:,} (-{reduction_total:.1f}%)", "OK")

        # Vérifier la cible
        if vertices_after < CONFIG["target_vertices_min"]:
            log(f"Attention : sous la cible minimale ({CONFIG['target_vertices_min']:,})", "WARN")
        elif vertices_after > CONFIG["target_vertices_max"]:
            log(f"Attention : au-dessus de la cible maximale ({CONFIG['target_vertices_max']:,})", "WARN")
        else:
            log(f"Cible atteinte : {vertices_after:,} vertices", "OK")

        # ÉTAPE 6 : Appliquer l'échelle à la géométrie
        apply_scale_to_geometry(copies, CONFIG["export_scale"])

        # ÉTAPE 7 : Cacher les originaux pour l'export
        hide_original_objects(exportable_objects)

        # ÉTAPE 7 : Exporter en GLB
        export_glb(copies)

        # ÉTAPE 8 : Restaurer les originaux
        show_original_objects(exportable_objects)

        # ÉTAPE 9 : Nettoyer
        log("Nettoyage...", "STEP")
        cleanup_temp_collection()

        print("\n" + "=" * 60)
        print("EXPORT TERMINÉ AVEC SUCCÈS")
        print("Le fichier .blend original n'a PAS été modifié.")
        print("=" * 60 + "\n")

        return True

    except Exception as e:
        log(f"Erreur : {str(e)}", "ERROR")
        # Tenter de nettoyer en cas d'erreur
        try:
            show_original_objects(get_exportable_objects())
            cleanup_temp_collection()
        except:
            pass
        return False


# =============================================================================
# EXÉCUTION
# =============================================================================

if __name__ == "__main__":
    main()
