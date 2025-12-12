# Commentaire d'intégration pédagogique

## Nature du module

Ce module est un **parcours exploratoire guidé**, et non une simulation fonctionnelle.

### Ce qu'il fait
- Présente l'architecture d'un moteur Hemi via 4 points d'intérêt
- Guide l'apprenant dans une découverte progressive (vue globale → détails)
- Permet une manipulation libre du modèle 3D (rotation, zoom)
- Propose une expérience AR pour contextualiser l'objet dans l'espace réel

### Ce qu'il ne fait pas
- Ne simule pas le fonctionnement mécanique (pistons, cycles)
- Ne propose pas d'évaluation ou de quiz
- Ne détaille pas les pièces internes non visibles
- Ne remplace pas un cours théorique sur la mécanique

---

## Insertion dans un parcours de formation

### Positionnement recommandé

```
[Introduction théorique]
        ↓
[MODULE AR : Exploration guidée] ← vous êtes ici
        ↓
[Approfondissement technique]
        ↓
[Évaluation / mise en pratique]
```

### Objectifs pédagogiques couverts

| Objectif | Niveau | Couvert |
|----------|--------|---------|
| Identifier les composants principaux d'un moteur | Connaissance | Oui |
| Situer spatialement les éléments | Compréhension | Oui |
| Comprendre la spécificité Hemi | Compréhension | Oui |
| Expliquer le fonctionnement détaillé | Analyse | Non |
| Diagnostiquer une panne | Application | Non |

### Prérequis pour l'apprenant
- Notion de base sur ce qu'est un moteur à combustion
- Aucune compétence technique spécifique requise

### Durée estimée
- Exploration libre : 2-5 minutes
- Avec lecture attentive des annotations : 5-8 minutes

---

## Pourquoi un module exploratoire (et non une simulation)

### Raisons pédagogiques

1. **Ancrage spatial prioritaire**
   Avant de comprendre "comment ça marche", l'apprenant doit pouvoir répondre à "c'est quoi et où c'est".

2. **Charge cognitive maîtrisée**
   4 points d'attention = mémorisation réaliste. Une simulation ajouterait des variables (mouvement, timing) qui dilueraient l'objectif.

3. **Autonomie de l'apprenant**
   L'ordre est suggéré, pas imposé. L'apprenant peut explorer selon son intérêt, revenir en arrière, zoomer sur un détail.

### Raisons techniques

1. **Robustesse**
   Moins de code = moins de bugs. Un module statique fonctionne sur tous les appareils supportant Model-Viewer.

2. **Maintenabilité**
   Les textes pédagogiques peuvent être modifiés sans toucher au modèle 3D. Le fichier `hotspots-config.json` centralise le contenu.

3. **Évolutivité**
   Ce module peut servir de base pour un parcours plus complet (ajout de modules, liens vers ressources externes).

---

## Structure des fichiers

```
Essai AR/
├── index.html                    ← page principale
├── assets/
│   └── hemi_engine.glb          ← modèle 3D (à générer)
├── hotspots/
│   └── hotspots-config.json     ← configuration des points d'intérêt
├── docs/
│   └── integration-pedagogique.md ← ce document
└── scripts/
    └── analyze_blend.py         ← script d'analyse Blender
```

---

## Utilisation

### Test local

```bash
# Serveur local simple (Python)
cd "/Users/fredericbourouliou/Essai AR"
python3 -m http.server 8000

# Ouvrir dans le navigateur
# http://localhost:8000
```

### Test AR

- **iOS** : Safari ouvre automatiquement Quick Look
- **Android** : Chrome utilise Scene Viewer
- Nécessite HTTPS en production (ou localhost pour les tests)

---

## Évolutions possibles (hors scope actuel)

Ces évolutions ne sont pas incluses dans le module actuel, mais pourraient être envisagées dans une version ultérieure :

- Audio descriptif pour chaque hotspot
- Mode "visite guidée" automatique
- Liens vers documentation technique externe
- Version multilingue
- Tracking d'usage (temps passé par hotspot)

---

## Limites connues

| Limite | Impact | Contournement |
|--------|--------|---------------|
| Positions hotspots approximatives | Ajustement visuel nécessaire | À calibrer après export GLB |
| Pas de persistance utilisateur | L'apprenant ne peut pas sauvegarder sa progression | Hors scope pour un module démo |
| AR non supportée sur tous les appareils | Certains utilisateurs n'auront que la vue 3D | La vue 3D reste pleinement fonctionnelle |

---

## Conclusion

Ce module remplit un rôle précis : **permettre à un apprenant de se repérer visuellement dans l'architecture d'un moteur Hemi**.

Il ne prétend pas enseigner la mécanique, mais offre un support visuel et spatial qui complète un enseignement théorique. Sa simplicité est un choix délibéré, garantissant robustesse et accessibilité.
