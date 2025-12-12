# Guide d'export GLB - Moteur Hemi

## Vue d'ensemble

Ce document explique le fonctionnement du script `export_glb.py` et fournit une checklist pour l'exécuter en toute sécurité.

---

## Principe de non-destructivité

Le script garantit que le fichier `hemi_engine.blend` original reste **intact** :

```
hemi_engine.blend (original)
        │
        ├── [LECTURE] Identification des objets
        │
        ▼
Collection temporaire "__EXPORT_TEMP__"
        │
        ├── Copies des objets (engine_export, etc.)
        ├── Décimation appliquée aux copies
        │
        ▼
assets/hemi_engine.glb (export)
        │
        ▼
Suppression de la collection temporaire
        │
        ▼
hemi_engine.blend (inchangé)
```

---

## Explication des étapes

### Étape 1 : Identification des objets exportables

**Ce qui se passe :**
- Le script parcourt tous les objets de la scène
- Il exclut les objets listés dans `CONFIG["exclude_objects"]`
- Il ne garde que les types MESH et CURVE

**Objets exclus :**
| Objet | Raison |
|-------|--------|
| Plane | Sol de la scène, inutile en AR |
| Camera | Objet de rendu Blender |
| Lamp, Lamp.001, Lamp.002 | Éclairage de scène |
| engine.009 | Mesh vide (0 vertices) |
| BezierCurve | Câbles décoratifs, complexité inutile |

**Objets exportés :**
- engine (corps principal)
- engine.001 à engine.008, engine.010, engine.011

---

### Étape 2 : Calcul des ratios de décimation

**Stratégie : décimation proportionnelle**

Plutôt que d'appliquer un ratio fixe à tous les objets, le script :
1. Calcule le nombre total de vertices des objets décimables
2. Détermine le ratio global pour atteindre la cible (65k vertices)
3. Applique ce même ratio à tous les objets au-dessus du seuil

**Pourquoi cette stratégie ?**
- Préserve les **détails relatifs** de chaque composant
- Un petit objet détaillé (500 vertices) garde ses 500 vertices
- Un gros objet (90k vertices) est réduit proportionnellement

**Seuil de décimation : 500 vertices**
- Les objets sous ce seuil ne sont pas décimés
- Évite de détruire les petits détails

**Calcul pour le moteur Hemi :**
```
Vertices actuels : ~203,000
Cible           : 65,000
Ratio global    : 65,000 / 203,000 ≈ 0.32 (32%)

Chaque objet conserve ~32% de ses vertices
```

---

### Étape 3 : Création de la collection temporaire

**Ce qui se passe :**
- Crée une collection nommée `__EXPORT_TEMP__`
- Si elle existe déjà (export précédent échoué), elle est supprimée d'abord

**Pourquoi une collection temporaire ?**
- Isole les copies des originaux
- Permet de tout nettoyer facilement à la fin
- Visible dans l'Outliner pendant l'export (pour debug)

---

### Étape 4 : Duplication des objets

**Ce qui se passe :**
- Chaque objet est copié avec `obj.copy()`
- Les données mesh sont aussi copiées avec `obj.data.copy()`
- Les copies sont nommées `{nom}_export`

**Point clé : copie des données**
```python
obj_copy = obj.copy()           # Copie l'objet
obj_copy.data = obj.data.copy() # Copie le mesh (crucial !)
```

Sans la copie du mesh, la décimation affecterait l'original.

---

### Étape 5 : Application de la décimation

**Ce qui se passe :**
- Pour chaque copie, un modifier `Decimate` est ajouté
- Type : COLLAPSE (fusion de vertices)
- Le modifier est ensuite appliqué (`modifier_apply`)

**Paramètres du Decimate :**
| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| decimate_type | COLLAPSE | Meilleure préservation de la forme |
| ratio | 0.32 (calculé) | Atteindre la cible de vertices |
| use_collapse_triangulate | False | Garde les quads si possible |

**Pourquoi appliquer le modifier ?**
- L'export GLB ne prend pas en compte les modifiers non appliqués
- Comme on travaille sur des copies, c'est sans risque

---

### Étape 6 : Masquage des originaux

**Ce qui se passe :**
- Les objets originaux sont cachés (`hide_set(True)`)
- Cela évite qu'ils soient inclus dans l'export

**Pourquoi ne pas les supprimer ?**
- On veut pouvoir les restaurer
- Le masquage est réversible instantanément

---

### Étape 7 : Export GLB

**Paramètres d'export :**

| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| export_format | GLB | Format binaire, fichier unique |
| use_selection | True | Exporte uniquement les copies sélectionnées |
| export_texcoords | True | Conserve les UV maps |
| export_normals | True | Conserve les normales pour l'éclairage |
| export_materials | EXPORT | Inclut les matériaux |
| export_cameras | False | Pas de caméra dans le GLB |
| export_lights | False | Model-Viewer gère l'éclairage |
| export_draco | True | Compression pour réduire la taille |

**Compression Draco :**
- Réduit significativement la taille du fichier (30-50%)
- Niveau 6 = bon compromis qualité/compression
- Supporté nativement par Model-Viewer

---

### Étape 8 : Restauration des originaux

**Ce qui se passe :**
- Les objets originaux sont à nouveau visibles
- `hide_set(False)` et `hide_render = False`

---

### Étape 9 : Nettoyage

**Ce qui se passe :**
- Tous les objets de la collection temporaire sont supprimés
- Les données mesh orphelines sont supprimées
- La collection elle-même est supprimée

**Résultat final :**
- Le fichier .blend est dans son état initial
- Le fichier GLB est créé dans `assets/`

---

## Checklist d'exécution

### Avant l'export

- [ ] **Sauvegarder le fichier .blend**
  - Le script refuse de s'exécuter si le fichier n'est pas sauvegardé
  - Faire une copie de backup si souhaité

- [ ] **Vérifier l'espace disque**
  - Le GLB fera environ 2-5 Mo
  - Le processus peut utiliser temporairement plus de mémoire

- [ ] **Fermer les éditeurs inutiles**
  - Libère de la mémoire pour le traitement

### Exécution

1. **Ouvrir le fichier dans Blender**
   ```
   File > Open > hemi_engine.blend
   ```

2. **Ouvrir l'éditeur de scripts**
   ```
   Onglet "Scripting" en haut de l'interface
   ```

3. **Charger le script**
   ```
   Text Editor > Open > scripts/export_glb.py
   ```

4. **Exécuter le script**
   ```
   Run Script (bouton ▶) ou Alt+P
   ```

5. **Observer la console**
   ```
   Window > Toggle System Console (Windows)
   ou voir le Terminal (macOS/Linux)
   ```

### Vérifications post-export

- [ ] **Fichier créé ?**
  ```
  ls -la assets/hemi_engine.glb
  ```

- [ ] **Taille raisonnable ?**
  - Attendu : 2-5 Mo avec Draco
  - Si > 10 Mo : vérifier la décimation

- [ ] **Fichier .blend intact ?**
  - Tous les objets originaux visibles
  - Pas de collection `__EXPORT_TEMP__` résiduelle

- [ ] **Test dans Model-Viewer ?**
  ```bash
  cd "/Users/fredericbourouliou/Essai AR"
  python3 -m http.server 8000
  # Ouvrir http://localhost:8000
  ```

### En cas de problème

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| Collection `__EXPORT_TEMP__` reste | Script interrompu | Supprimer manuellement dans l'Outliner |
| Objets originaux cachés | Script interrompu | Sélectionner tout (A) > Alt+H pour révéler |
| Export vide | Mauvaise sélection | Vérifier `CONFIG["exclude_objects"]` |
| Fichier trop gros | Draco désactivé | Vérifier `CONFIG["use_draco"]` |
| Erreur "not saved" | Fichier non sauvegardé | File > Save |

---

## Exécution en ligne de commande

Pour automatiser ou intégrer dans un pipeline :

```bash
cd "/Users/fredericbourouliou/Essai AR"

/Applications/Blender.app/Contents/MacOS/Blender \
  hemi_engine.blend \
  --background \
  --python scripts/export_glb.py
```

**Options utiles :**
- `--background` : pas d'interface graphique
- `--python` : exécute le script
- Ajouter `2>&1 | tee export.log` pour logger

---

## Résumé des garanties

| Garantie | Comment |
|----------|---------|
| Fichier original intact | Travail sur copies uniquement |
| Décimation réversible | Appliquée aux copies, pas aux originaux |
| Nettoyage automatique | Collection temporaire supprimée |
| Échec sécurisé | Try/catch avec restauration des originaux |
| Traçabilité | Logs détaillés dans la console |
