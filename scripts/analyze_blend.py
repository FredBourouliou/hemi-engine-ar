"""
Script d'analyse non-destructif pour fichier .blend
À exécuter dans Blender : File > Open > hemi_engine.blend
Puis : Scripting > New > Coller ce script > Run Script

Le rapport sera généré dans le même dossier que le fichier .blend
"""

import bpy
import mathutils
import os
import json
from datetime import datetime

def analyze_blend_file():
    """Analyse complète du fichier .blend ouvert"""

    report = {
        "meta": {
            "fichier": bpy.data.filepath,
            "date_analyse": datetime.now().isoformat(),
            "version_blender": bpy.app.version_string
        },
        "statistiques": {},
        "objets": [],
        "materiaux": [],
        "textures": [],
        "collections": [],
        "animations": [],
        "dimensions_scene": {}
    }

    # --- STATISTIQUES GÉNÉRALES ---
    report["statistiques"] = {
        "nombre_objets": len(bpy.data.objects),
        "nombre_meshes": len(bpy.data.meshes),
        "nombre_materiaux": len(bpy.data.materials),
        "nombre_textures": len(bpy.data.textures),
        "nombre_images": len(bpy.data.images),
        "nombre_collections": len(bpy.data.collections),
        "nombre_animations": len(bpy.data.actions)
    }

    # --- ANALYSE DES OBJETS ---
    for obj in bpy.data.objects:
        obj_info = {
            "nom": obj.name,
            "type": obj.type,
            "visible": obj.visible_get(),
            "parent": obj.parent.name if obj.parent else None,
            "location": list(obj.location),
            "dimensions": list(obj.dimensions),
            "materiaux_assignes": []
        }

        # Matériaux assignés
        if hasattr(obj, 'material_slots'):
            for slot in obj.material_slots:
                if slot.material:
                    obj_info["materiaux_assignes"].append(slot.material.name)

        # Infos mesh si applicable
        if obj.type == 'MESH' and obj.data:
            mesh = obj.data
            obj_info["mesh"] = {
                "vertices": len(mesh.vertices),
                "faces": len(mesh.polygons),
                "edges": len(mesh.edges),
                "uv_layers": [uv.name for uv in mesh.uv_layers]
            }

        report["objets"].append(obj_info)

    # --- ANALYSE DES MATÉRIAUX ---
    for mat in bpy.data.materials:
        mat_info = {
            "nom": mat.name,
            "use_nodes": mat.use_nodes,
            "textures_utilisees": []
        }

        # Recherche des textures dans les nodes
        if mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    mat_info["textures_utilisees"].append({
                        "nom_image": node.image.name,
                        "chemin": node.image.filepath,
                        "packed": node.image.packed_file is not None
                    })

        report["materiaux"].append(mat_info)

    # --- ANALYSE DES COLLECTIONS ---
    for col in bpy.data.collections:
        col_info = {
            "nom": col.name,
            "objets": [obj.name for obj in col.objects]
        }
        report["collections"].append(col_info)

    # --- ANALYSE DES ANIMATIONS ---
    for action in bpy.data.actions:
        action_info = {
            "nom": action.name,
            "frame_range": [action.frame_range[0], action.frame_range[1]],
            "nombre_fcurves": len(action.fcurves)
        }
        report["animations"].append(action_info)

    # --- DIMENSIONS GLOBALES DE LA SCÈNE ---
    if bpy.data.objects:
        min_coords = [float('inf')] * 3
        max_coords = [float('-inf')] * 3

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for corner in obj.bound_box:
                    world_corner = obj.matrix_world @ mathutils.Vector(corner)
                    for i in range(3):
                        min_coords[i] = min(min_coords[i], world_corner[i])
                        max_coords[i] = max(max_coords[i], world_corner[i])

        if min_coords[0] != float('inf'):
            report["dimensions_scene"] = {
                "min": min_coords,
                "max": max_coords,
                "taille": [max_coords[i] - min_coords[i] for i in range(3)],
                "unite": bpy.context.scene.unit_settings.length_unit
            }

    return report


def generate_report():
    """Génère le rapport en JSON et en texte lisible"""

    report = analyze_blend_file()

    # Chemin de sortie
    blend_dir = os.path.dirname(bpy.data.filepath) or os.getcwd()
    json_path = os.path.join(blend_dir, "analyse_blend_report.json")
    txt_path = os.path.join(blend_dir, "analyse_blend_report.txt")

    # Export JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Export texte lisible
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("RAPPORT D'ANALYSE DU FICHIER BLEND\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Fichier : {report['meta']['fichier']}\n")
        f.write(f"Date : {report['meta']['date_analyse']}\n")
        f.write(f"Blender : {report['meta']['version_blender']}\n\n")

        f.write("-" * 40 + "\n")
        f.write("STATISTIQUES\n")
        f.write("-" * 40 + "\n")
        for key, val in report['statistiques'].items():
            f.write(f"  {key}: {val}\n")

        f.write("\n" + "-" * 40 + "\n")
        f.write("OBJETS MESH (avec polygones)\n")
        f.write("-" * 40 + "\n")
        for obj in report['objets']:
            if obj['type'] == 'MESH' and 'mesh' in obj:
                f.write(f"\n  [{obj['nom']}]\n")
                f.write(f"    Vertices: {obj['mesh']['vertices']}\n")
                f.write(f"    Faces: {obj['mesh']['faces']}\n")
                f.write(f"    Dimensions: {[round(d, 3) for d in obj['dimensions']]}\n")
                f.write(f"    Matériaux: {obj['materiaux_assignes']}\n")
                f.write(f"    UV Maps: {obj['mesh']['uv_layers']}\n")

        f.write("\n" + "-" * 40 + "\n")
        f.write("MATÉRIAUX\n")
        f.write("-" * 40 + "\n")
        for mat in report['materiaux']:
            f.write(f"\n  [{mat['nom']}]\n")
            f.write(f"    Nodes: {mat['use_nodes']}\n")
            if mat['textures_utilisees']:
                for tex in mat['textures_utilisees']:
                    f.write(f"    Texture: {tex['nom_image']} (packed: {tex['packed']})\n")

        if report['dimensions_scene']:
            f.write("\n" + "-" * 40 + "\n")
            f.write("DIMENSIONS GLOBALES\n")
            f.write("-" * 40 + "\n")
            dims = report['dimensions_scene']
            f.write(f"  Taille X: {dims['taille'][0]:.3f} {dims['unite']}\n")
            f.write(f"  Taille Y: {dims['taille'][1]:.3f} {dims['unite']}\n")
            f.write(f"  Taille Z: {dims['taille'][2]:.3f} {dims['unite']}\n")

        if report['animations']:
            f.write("\n" + "-" * 40 + "\n")
            f.write("ANIMATIONS\n")
            f.write("-" * 40 + "\n")
            for anim in report['animations']:
                f.write(f"  {anim['nom']}: frames {anim['frame_range']}\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("Rapport JSON complet : analyse_blend_report.json\n")
        f.write("=" * 60 + "\n")

    print("\n" + "=" * 50)
    print("ANALYSE TERMINÉE")
    print("=" * 50)
    print(f"Rapport JSON : {json_path}")
    print(f"Rapport texte : {txt_path}")
    print("=" * 50)

    return report


# Exécution
if __name__ == "__main__":
    generate_report()
