# Moteur Hemi - Exploration AR

Module pedagogique en realite augmentee pour l'exploration d'un moteur Hemi V8.

## Demo

[https://fredbourouliou.github.io](https://fredbourouliou.github.io)

## Fonctionnalites

- Visualisation 3D interactive du moteur
- Mode AR sur mobile (iOS Safari, Android Chrome)
- 3 hotspots pedagogiques interactifs :
  1. Blower (suralimentation)
  2. Culasse hemispherique
  3. Collecteur d'echappement
- Bandeau de consigne pedagogique
- Legende des composants

### Limites AR (assumees)

L'AR via Quick Look (iOS) et Scene Viewer (Android) permet uniquement :
- Placement a l'echelle reelle
- Deplacement physique autour de l'objet

Les hotspots et interactions sont disponibles en mode 2D uniquement.

## Stack technique

- [Model-Viewer](https://modelviewer.dev/) - Composant web Google pour 3D/AR
- HTML/CSS/JS vanilla
- Modele 3D : GLB (exporte depuis Blender)

## Structure du projet

```
.
├── index.html                    # Page principale
├── assets/
│   ├── models/
│   │   └── hemi_engine.glb       # Modele 3D optimise
│   ├── styles/
│   │   └── styles.css            # Styles du module
│   └── js/
│       └── app.js                # Logique JS (hotspots, accessibilite)
├── scripts/
│   ├── analyze_blend.py          # Analyse du fichier Blender
│   └── export_glb.py             # Export GLB non-destructif
├── docs/
│   ├── integration-pedagogique.md
│   └── export-glb-guide.md
└── hemi_engine.blend             # Fichier source Blender
```

## Utilisation locale

```bash
# Serveur local
python3 -m http.server 8000

# Ouvrir http://localhost:8000
```

## Export du modele 3D

Le script `scripts/export_glb.py` permet d'exporter le fichier Blender en GLB optimise :

```bash
/Applications/Blender.app/Contents/MacOS/Blender hemi_engine.blend --background --python scripts/export_glb.py
```

Caracteristiques de l'export :
- Non-destructif (fichier .blend intact)
- Decimation automatique (~65k vertices)
- Exclusion des objets non pertinents (camera, lampes, sol)

## Compatibilite AR

| Plateforme | Navigateur | Support |
|------------|------------|---------|
| iOS | Safari | Quick Look |
| Android | Chrome | Scene Viewer |
| Desktop | Tous | Vue 3D uniquement |

## Objectifs pedagogiques

Ce module permet de :
- Identifier les composants principaux d'un moteur V8
- Comprendre la specificite de l'architecture Hemi
- Visualiser le systeme de suralimentation
- Situer les circuits d'admission et d'echappement

## Licence

MIT
