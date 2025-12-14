# Moteur Hemi - Module AR Pedagogique

Module pedagogique d'inspection 3D et AR pour l'exploration d'un moteur Hemi V8.

## Demo

[https://fredbourouliou.github.io](https://fredbourouliou.github.io)

## Fonctionnalites

### Structure pedagogique en 5 phases

| Phase | Nom | Description |
|-------|-----|-------------|
| 0 | Contexte | Introduction et exploration libre |
| 1 | Vue globale | Identification des sous-ensembles |
| 2 | Inspection | Observation sans blower |
| 3 | Structure | Analyse du bloc moteur seul |
| 4 | Synthese | Vision complete avec reperage |

### 3 etats pedagogiques (GLB distincts)

- **Etat A** : Moteur complet (vue d'ensemble)
- **Etat B** : Sans blower (bloc visible)
- **Etat C** : Bloc seul (structure de base)

### Autres fonctionnalites

- Visualisation 3D interactive
- Mode AR sur mobile (iOS Safari, Android Chrome)
- Hotspot pedagogique (Blower)
- Bandeau de consigne dynamique
- Legende des composants

### Limites AR (assumees)

L'AR via Quick Look (iOS) et Scene Viewer (Android) permet uniquement :
- Placement a l'echelle reelle
- Deplacement physique autour de l'objet

Les hotspots, changements d'etat et interactions sont disponibles en mode 2D uniquement.

## Stack technique

- [Model-Viewer](https://modelviewer.dev/) - Composant web Google pour 3D/AR
- HTML/CSS/JS vanilla (aucun framework)
- Modeles 3D : GLB (exportes depuis Blender)

## Structure du projet

```
.
├── index.html                         # Page principale
├── assets/
│   ├── models/
│   │   ├── hemi_state_a_full.glb      # Etat A - Complet
│   │   ├── hemi_state_b_no_blower.glb # Etat B - Sans blower
│   │   └── hemi_state_c_bloc.glb      # Etat C - Bloc seul
│   ├── styles/
│   │   └── styles.css
│   └── js/
│       └── app.js                     # Logique etats/phases
├── scripts/
│   ├── analyze_blend.py               # Analyse fichier Blender
│   ├── export_glb.py                  # Export GLB simple
│   └── export_states.py               # Export multi-etats
├── docs/
│   ├── integration-pedagogique.md
│   └── export-glb-guide.md
└── hemi_engine.blend                  # Fichier source Blender
```

## Utilisation locale

```bash
# Serveur local
cd "/Users/fredericbourouliou/Essai AR"
python3 -m http.server 8000

# Ouvrir http://localhost:8000
```

## Export des modeles 3D

### Export multi-etats (recommande)

```bash
/Applications/Blender.app/Contents/MacOS/Blender hemi_engine.blend --background --python scripts/export_states.py
```

Genere 3 GLB correspondant aux etats pedagogiques A, B et C.

### Configuration des etats

Modifier `scripts/export_states.py` pour ajuster :
- Les objets exclus par etat
- Les noms de fichiers
- Les descriptions

## Compatibilite

| Plateforme | Navigateur | Support |
|------------|------------|---------|
| iOS | Safari | Quick Look (AR) |
| Android | Chrome | Scene Viewer (AR) |
| Desktop | Tous | Vue 3D uniquement |

## Objectifs pedagogiques

Ce module permet de :
- Identifier les composants principaux d'un moteur V8
- Comprendre la specificite de l'architecture Hemi
- Visualiser le systeme de suralimentation (blower)
- Observer la structure interne du bloc moteur
- Suivre une progression pedagogique guidee

## Licence

MIT
