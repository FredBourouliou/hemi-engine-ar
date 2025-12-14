"""
===============================================================================
SCRIPT D'EXPORT MULTI-ÉTATS GLB
===============================================================================

Projet     : AR Pédagogique - Moteur Hemi
Fichier    : export_states.py
Sortie     : assets/models/hemi_state_*.glb

ÉTATS PÉDAGOGIQUES :
--------------------
- État A (full)      : Moteur complet
- État B (no_blower) : Sans suralimentation (blower)
- État C (bloc)      : Bloc moteur seul

USAGE :
-------
/Applications/Blender.app/Contents/MacOS/Blender hemi_engine.blend --background --python scripts/export_states.py

===============================================================================
"""

import bpy
import os

# =============================================================================
# CONFIGURATION DES ÉTATS
# =============================================================================

STATES_CONFIG = {
    "state_a_full": {
        "filename": "hemi_state_a_full.glb",
        "description": "Moteur complet",
        "exclude_objects": []  # Aucune exclusion
    },
    "state_b_no_blower": {
        "filename": "hemi_state_b_no_blower.glb",
        "description": "Sans blower (suralimentation)",
        "exclude_objects": ["engine.001"]  # Blower
    },
    "state_c_bloc": {
        "filename": "hemi_state_c_bloc.glb",
        "description": "Bloc moteur seul",
        "exclude_objects": [
            "engine.001",  # Blower
            "engine.006",  # Échappement/admission
            "engine.007",  # Échappement/admission
            "engine.008",  # Accessoires
        ]
    }
}

# Configuration globale
GLOBAL_CONFIG = {
    "output_dir": "assets/models",
    "exclude_always": [
        "Plane",
        "Camera",
        "Lamp", "Lamp.001", "Lamp.002",
        "engine.009",  # Mesh vide
        "BezierCurve",
    ],
    "target_vertices": 65000,
    "decimation_threshold": 500,
    "export_scale": 0.05,
    "temp_collection_name": "__EXPORT_TEMP__",
}


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def log(message, level="INFO"):
    prefix = {
        "INFO": "[INFO]",
        "WARN": "[ATTENTION]",
        "ERROR": "[ERREUR]",
        "OK": "[OK]",
        "STEP": ">>>"
    }.get(level, "[INFO]")
    print(f"{prefix} {message}")


def count_vertices(objects):
    total = 0
    for obj in objects:
        if obj.type == 'MESH' and obj.data:
            total += len(obj.data.vertices)
    return total


def get_exportable_objects(state_exclude_list):
    """Retourne les objets à exporter pour un état donné."""
    exportable = []
    excluded = GLOBAL_CONFIG["exclude_always"] + state_exclude_list

    for obj in bpy.data.objects:
        if obj.name in excluded:
            continue
        if obj.type in ['MESH', 'CURVE']:
            exportable.append(obj)

    return exportable


def calculate_decimation_ratios(objects, target_vertices):
    decimatable_vertices = 0
    non_decimatable_vertices = 0

    for obj in objects:
        if obj.type != 'MESH' or not obj.data:
            continue
        v_count = len(obj.data.vertices)
        if v_count >= GLOBAL_CONFIG["decimation_threshold"]:
            decimatable_vertices += v_count
        else:
            non_decimatable_vertices += v_count

    if decimatable_vertices == 0:
        return {}

    target_for_decimatable = target_vertices - non_decimatable_vertices
    if target_for_decimatable <= 0:
        return {}

    global_ratio = target_for_decimatable / decimatable_vertices
    global_ratio = max(0.1, min(1.0, global_ratio))

    ratios = {}
    for obj in objects:
        if obj.type != 'MESH' or not obj.data:
            continue
        v_count = len(obj.data.vertices)
        if v_count >= GLOBAL_CONFIG["decimation_threshold"]:
            ratios[obj.name] = global_ratio
        else:
            ratios[obj.name] = 1.0

    return ratios


# =============================================================================
# FONCTIONS D'EXPORT
# =============================================================================

def create_temp_collection():
    temp_name = GLOBAL_CONFIG["temp_collection_name"]

    if temp_name in bpy.data.collections:
        old_collection = bpy.data.collections[temp_name]
        for obj in list(old_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old_collection)

    temp_collection = bpy.data.collections.new(temp_name)
    bpy.context.scene.collection.children.link(temp_collection)
    return temp_collection


def duplicate_objects(objects, target_collection):
    copies = {}
    for obj in objects:
        obj_copy = obj.copy()
        if obj.data:
            obj_copy.data = obj.data.copy()
        obj_copy.name = f"{obj.name}_export"
        target_collection.objects.link(obj_copy)
        copies[obj.name] = obj_copy
    return copies


def apply_decimation(copies, ratios):
    for original_name, obj_copy in copies.items():
        if obj_copy.type != 'MESH':
            continue

        ratio = ratios.get(original_name, 1.0)
        if ratio >= 0.99:
            continue

        bpy.ops.object.select_all(action='DESELECT')
        obj_copy.select_set(True)
        bpy.context.view_layer.objects.active = obj_copy

        decimate = obj_copy.modifiers.new(name="Decimate_Export", type='DECIMATE')
        decimate.decimate_type = 'COLLAPSE'
        decimate.ratio = ratio

        bpy.ops.object.modifier_apply(modifier="Decimate_Export")


def apply_scale(copies, scale_factor):
    if not copies:
        return

    bpy.ops.object.select_all(action='DESELECT')
    for obj_copy in copies.values():
        obj_copy.select_set(True)

    bpy.context.view_layer.objects.active = list(copies.values())[0]

    original_pivot = bpy.context.scene.tool_settings.transform_pivot_point
    original_cursor = bpy.context.scene.cursor.location.copy()

    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'

    bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.context.scene.cursor.location = original_cursor
    bpy.context.scene.tool_settings.transform_pivot_point = original_pivot


def export_glb(copies, output_path):
    bpy.ops.object.select_all(action='DESELECT')
    for obj_copy in copies.values():
        obj_copy.select_set(True)

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
    except TypeError:
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            use_selection=True,
            export_format='GLB'
        )

    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        log(f"Exporté : {output_path} ({file_size:.2f} Mo)", "OK")
        return True
    return False


def cleanup_temp_collection():
    temp_name = GLOBAL_CONFIG["temp_collection_name"]

    if temp_name not in bpy.data.collections:
        return

    temp_collection = bpy.data.collections[temp_name]

    for obj in list(temp_collection.objects):
        if obj.data and obj.data.users == 1:
            if obj.type == 'MESH':
                bpy.data.meshes.remove(obj.data)
            elif obj.type == 'CURVE':
                bpy.data.curves.remove(obj.data)
        else:
            bpy.data.objects.remove(obj, do_unlink=True)

    bpy.data.collections.remove(temp_collection)


def hide_objects(objects):
    for obj in objects:
        obj.hide_set(True)
        obj.hide_render = True


def show_objects(objects):
    for obj in objects:
        obj.hide_set(False)
        obj.hide_render = False


# =============================================================================
# EXPORT D'UN ÉTAT
# =============================================================================

def export_state(state_name, state_config):
    """Exporte un état pédagogique en GLB."""

    log(f"\n{'='*50}", "INFO")
    log(f"EXPORT ÉTAT : {state_name}", "STEP")
    log(f"Description : {state_config['description']}", "INFO")
    log(f"Exclusions : {state_config['exclude_objects']}", "INFO")
    log(f"{'='*50}", "INFO")

    # Objets à exporter
    exportable = get_exportable_objects(state_config['exclude_objects'])
    if not exportable:
        log("Aucun objet à exporter", "ERROR")
        return False

    log(f"Objets à exporter : {len(exportable)}", "OK")

    vertices_before = count_vertices(exportable)

    # Calcul décimation
    ratios = calculate_decimation_ratios(exportable, GLOBAL_CONFIG["target_vertices"])

    # Collection temporaire
    temp_collection = create_temp_collection()

    # Dupliquer
    copies = duplicate_objects(exportable, temp_collection)

    # Décimer
    apply_decimation(copies, ratios)

    vertices_after = count_vertices(list(copies.values()))
    log(f"Vertices : {vertices_before:,} -> {vertices_after:,}", "INFO")

    # Échelle
    apply_scale(copies, GLOBAL_CONFIG["export_scale"])

    # Cacher originaux
    hide_objects(exportable)

    # Export
    blend_dir = os.path.dirname(bpy.data.filepath) or os.getcwd()
    output_dir = os.path.join(blend_dir, GLOBAL_CONFIG["output_dir"])
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, state_config["filename"])
    success = export_glb(copies, output_path)

    # Restaurer
    show_objects(exportable)

    # Nettoyer
    cleanup_temp_collection()

    return success


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 60)
    print("EXPORT MULTI-ÉTATS - MOTEUR HEMI")
    print("=" * 60)

    if not bpy.data.filepath:
        log("Le fichier .blend doit être sauvegardé", "ERROR")
        return

    success_count = 0

    for state_name, state_config in STATES_CONFIG.items():
        try:
            if export_state(state_name, state_config):
                success_count += 1
        except Exception as e:
            log(f"Erreur état {state_name}: {e}", "ERROR")
            cleanup_temp_collection()

    print("\n" + "=" * 60)
    print(f"EXPORT TERMINÉ : {success_count}/{len(STATES_CONFIG)} états")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
