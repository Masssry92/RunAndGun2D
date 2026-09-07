# RunAndGun2D — TP02 ST2OOS (Unity 2D)

Mini-jeu Run & Gun 2D inspiré de Metal Slug, réalisé pour le TP02 du module
ST2OOS. Le joueur se déplace, saute et tire dans plusieurs directions à
travers deux niveaux peuplés d'ennemis de mêlée et à distance.

## 1. Ouvrir le projet

1. Installez **Unity Hub** puis l'éditeur **Unity 2022.3 LTS** (ou toute
   version 2022.3.x / 2023.x — le projet n'utilise aucune fonctionnalité
   récente exotique). Si Unity Hub propose une mise à jour de version à
   l'ouverture, acceptez : le projet s'ouvrira normalement.
2. Dans Unity Hub : **Add** → sélectionnez le dossier `RunAndGun2D` (celui
   qui contient `Assets/`, `Packages/`, `ProjectSettings/`).
3. Ouvrez le projet. Le premier import peut prendre quelques minutes
   (compilation des scripts, import des sprites).
4. Ouvrez `Assets/Scenes/Level01.unity` (double-clic) puis lancez **Play**.

## 2. Contrôles

| Action | Touche |
|---|---|
| Se déplacer | `A` / `D` |
| Sauter | `W` ou `Espace` |
| Viser | flèches directionnelles (`↑ ↓ ← →`, diagonales en combinant deux flèches) |
| Tirer | `Ctrl` gauche ou clic gauche de la souris |

Si aucune flèche n'est maintenue, le tir part automatiquement dans la
direction où le personnage regarde (gauche/droite).

## 3. Structure du projet

```
Assets/
  Animations/   -> Animator Controllers et Animation Clips (à ajouter, voir §6)
  Prefabs/      -> Player, EnemyMelee, EnemyRanged, PlayerProjectile,
                   EnemyProjectile, Platform, HealthPickup, AmmoPickup
  Scenes/       -> Level01.unity, Level02.unity
  Scripts/
    Player/     -> PlayerController, PlayerShooting, PlayerHealth
    Enemies/    -> EnemyBase (classe abstraite), EnemyMelee, EnemyRanged
    Combat/     -> Health, Projectile, DetectionZone, Team
    Level/      -> CameraFollow, LevelExitTrigger, CombatZoneActivator
    Managers/   -> GameManager, ScoreManager
    UI/         -> HealthBarUI
    Pickups/    -> PickupItem
  Sprites/      -> sprites placeholder générés (voir §6)
  UI/           -> sprites pour une éventuelle barre de vie
```

## 4. Où sont les notions demandées par le sujet

| Consigne du sujet | Implémentation |
|---|---|
| WASD, saut, orientation | `PlayerController.cs` (déplacement A/D, saut W/Espace, `SpriteRenderer.flipX`) |
| Animator Controller | Hooks prêts dans le code (`animator.SetFloat/SetTrigger`, protégés par `runtimeAnimatorController != null`) — controller à créer, voir §6 |
| Tir multidirectionnel | `PlayerShooting.cs` (direction = flèches, normalisée avec `Vector2.normalized`) + `Projectile.cs` |
| Rigidbody2D / Collider2D | Sur Player, ennemis, projectiles (`Rigidbody2D`, `BoxCollider2D`, `CircleCollider2D`) |
| Prefabs pour les éléments réutilisables | `Assets/Prefabs/*.prefab` (voir remarque §7) |
| Layers / Collision Matrix | Layers `Ground`, `PlayerProjectile`, `EnemyProjectile` déclarés dans le projet ; filtrage actif fait via les Tags (`Player`/`Enemy`/`Ground`) pour rester robuste sans configuration manuelle — voir §8 pour affiner avec de vrais Layers |
| Ennemi de mêlée | `EnemyMelee.cs` : détecte via `DetectionZone` (Trigger), se rapproche, attaque au contact |
| Ennemi à distance | `EnemyRanged.cs` : détecte via `DetectionZone`, tire des `Projectile` |
| Triggers (détection, attaque, activation de zone, fin de niveau) | `DetectionZone.cs`, `CombatZoneActivator.cs`, `LevelExitTrigger.cs` — tous basés sur `Collider2D.isTrigger = true` |
| Dégâts et vie | `Health.cs` (composant générique réutilisé par joueur et ennemis) |
| Au moins 2 niveaux, caméra qui suit | `Level01.unity`, `Level02.unity`, `CameraFollow.cs` |
| Organisation en dossiers | Voir §3 |

## 5. Ce qui est déjà en place dans les scènes

- **Level01** : sol avec un fossé à sauter, une plateforme flottante, un
  ennemi de mêlée en patrouille, une embuscade (mêlée + distance) activée
  par une `CombatZoneActivator`, un pickup de vie, et une zone de sortie
  vers `Level02`.
- **Level02** : progression verticale par paliers de plateformes, un
  ennemi à distance posté en hauteur, un ennemi de mêlée en fin de niveau,
  une embuscade supplémentaire, un pickup de munitions, et une sortie qui
  boucle vers `Level01` (à remplacer par un menu / Level03 si besoin).

## 6. Sprites placeholder — à remplacer

Les sprites (joueur, ennemis, projectiles, plateforme, pickups) sont des
formes simples générées automatiquement, **juste pour que le projet soit
jouable immédiatement sans dépendre d'assets externes**. Le sujet vous
laisse libres de choisir votre univers visuel (voir GameArt2D — Freebies).

Pour remplacer un sprite : glissez votre nouvelle image dans
`Assets/Sprites/` (mode Sprite (2D and UI), Sprite Mode = Single), puis
sur le prefab concerné (`Assets/Prefabs/...`), remplacez le sprite dans le
composant `Sprite Renderer`.

### Ajouter les animations

1. Sélectionnez le prefab (ex. `Player`) → **Add Component → Animator**.
2. Fenêtre **Window → Animation → Animator** : créez un
   *Animator Controller* (clic droit dans `Assets/Animations/` → Create →
   Animator Controller), glissez-le dans le champ `Controller` de
   l'Animator.
3. Créez vos clips (Idle, Run, Jump, Shoot...) et câblez les transitions
   avec les paramètres déjà utilisés par le code : `Speed` (float),
   `Grounded` (bool), `VerticalVelocity` (float), `Jump` (trigger),
   `Shoot` (trigger), `Attack` (trigger, ennemi de mêlée).
4. Rien d'autre à changer côté script : le code vérifie déjà
   `animator.runtimeAnimatorController != null` avant d'appeler l'Animator,
   donc tout fonctionne avec ou sans animations.

## 7. À propos des Prefabs et des scènes

Les Prefabs (`Assets/Prefabs/*.prefab`) sont de vrais assets réutilisables,
comme demandé par le sujet. Les instances placées dans `Level01`/`Level02`
sont des copies indépendantes (mêmes composants, mêmes scripts) plutôt que
des liens vers ces Prefabs, afin de garantir une ouverture fiable du projet.
Si vous voulez profiter du workflow Prefab habituel (modifier un Prefab et
voir toutes ses instances se mettre à jour), il suffit de supprimer une
instance dans la scène et de glisser le Prefab correspondant à la place —
cela prend une minute par objet.

## 8. Configuration manuelle recommandée (2 minutes)

Le gameplay fonctionne sans cette étape (les scripts utilisent des Tags et
des `LayerMask` réglés sur *Everything* par défaut), mais pour respecter
pleinement l'esprit de la consigne « Layers / Layer Collision Matrix » :

1. **Edit → Project Settings → Tags and Layers** : vérifiez que les tags
   `Player`, `Enemy`, `Ground` existent (déjà configurés) et assignez le
   layer `Ground` aux plateformes, `PlayerProjectile` / `EnemyProjectile`
   aux projectiles correspondants.
2. **Edit → Project Settings → Physics 2D** → *Layer Collision Matrix* :
   décochez par exemple `PlayerProjectile` × `Player` et
   `EnemyProjectile` × `Enemy` pour qu'un projectile ne puisse jamais
   toucher son propre camp par collision physique (les dégâts sont de
   toute façon filtrés par Tag dans `Projectile.cs`, donc c'est une
   sécurité supplémentaire, pas un prérequis).

## 9. Bonus déjà implémentés

- Système de munitions optionnel (`PlayerShooting.useAmmo`) + pickup de
  munitions.
- Score (`ScoreManager`) incrémenté à chaque ennemi éliminé.
- Pickups de vie et de munitions (`PickupItem.cs`).
- Zones d'embuscade activées par Trigger (`CombatZoneActivator.cs`).
- Cadence de tir réglable (`fireRate`) côté joueur et ennemi à distance.

Pistes pour aller plus loin : écran de Game Over visuel (le
`GameManager.ShowGameOver()` met déjà `Time.timeScale = 0`, il ne manque
qu'un Canvas UI à assigner dans le champ `Game Over Panel`), barre de vie
UI (`HealthBarUI.cs` est prêt, il suffit d'un Canvas avec une Image en
mode *Filled* liée au `Health` du joueur), sons et particules, boss.

## 10. Publier sur GitHub (pour le rendu)

```bash
cd RunAndGun2D
git init
git add .
git commit -m "TP02 - Run & Gun 2D"
git branch -M main
git remote add origin https://github.com/<votre-compte>/<votre-repo>.git
git push -u origin main
```

Le `.gitignore` fourni exclut déjà `Library/`, `Temp/`, `Obj/`,
`UserSettings/`, etc. — seuls les dossiers `Assets/`, `Packages/` et
`ProjectSettings/` (et ce README) doivent être versionnés. Pensez à
vérifier que le dépôt est bien **public** avant de rendre le lien, comme
demandé dans le sujet.

## 11. Note technique

Le contenu Unity de ce projet (fichiers `.prefab`, `.unity`, `.meta`) a
été généré de façon procédurale (scripts Python `build_*.py` et
`unity_yaml.py` à la racine, plus `gen_sprites.py` pour les sprites) afin
de produire un projet complet, cohérent et immédiatement ouvrable. Ces
scripts Python ne font pas partie du projet Unity lui-même : vous pouvez
les supprimer avant de rendre le projet, ou les garder à titre de
documentation de la génération.
