#!/usr/bin/env python3
"""Génère Assets/Scenes/Level01.unity et Level02.unity."""
import hashlib
import json
import os
from unity_yaml import UnityFile, ref_component

ROOT = "/home/claude/project/RunAndGun2D"
SCENES_DIR = os.path.join(ROOT, "Assets", "Scenes")
os.makedirs(SCENES_DIR, exist_ok=True)

with open(os.path.join(ROOT, "_guid_table.json")) as f:
    TABLE = json.load(f)

PREFAB_GUIDS = TABLE["prefabs"]
EXPORTS = TABLE["exports"]

SCENE_META = """fileFormatVersion: 2
guid: {guid}
DefaultImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""


def guid_for(path):
    return hashlib.md5(("RunAndGun2D::" + path).encode("utf-8")).hexdigest()


def fix_parent(u, transform_id, new_parent_id):
    marker = f"--- !u!4 &{transform_id}\n"
    for i, block in enumerate(u.blocks):
        if block.startswith(marker):
            u.blocks[i] = block.replace("m_Father: {fileID: 0}", f"m_Father: {{fileID: {new_parent_id}}}", 1)
            return
    raise RuntimeError(f"transform {transform_id} introuvable")


# ---------------------------------------------------------------------------
# Briques réutilisables (mêmes structures que dans build_prefabs.py, mais
# incorporées directement dans la scène plutôt qu'en tant qu'instances de
# prefab -- voir README pour l'explication de ce choix).
# ---------------------------------------------------------------------------

def add_ground_tile(u, x, y, name=None):
    go = u.new_go()
    tr = u.transform(go, position=(x, y, 0), parent=0)
    sr = u.sprite_renderer(go, "platform", order=0)
    col = u.box_collider2d(go, size=(1, 1))
    u.write_game_object(go, name or f"Ground_{x}_{y}", tag="Ground", component_ids=[tr, sr, col])
    return go


def add_platform_run(u, x_start, x_end, y):
    return [add_ground_tile(u, x, y) for x in range(x_start, x_end + 1)]


def add_player(u, x, y):
    root_go = u.new_go()
    gc_go = u.new_go()
    fp_go = u.new_go()

    gc_tr = u.transform(gc_go, position=(0, -0.34, 0), parent=None)
    fp_tr = u.transform(fp_go, position=(0.26, 0.05, 0), parent=None)

    sr = u.sprite_renderer(root_go, "player", order=5)
    rb = u.rigidbody2d(root_go, gravity_scale=3, fixed_rotation=True)
    col = u.box_collider2d(root_go, size=(0.42, 0.62))
    health_mb = u.monobehaviour(root_go, "Health", fields={"maxHealth": 5})
    controller_mb = u.monobehaviour(root_go, "PlayerController", fields={"groundCheck": ref_component(gc_tr)})
    shooting_mb = u.monobehaviour(root_go, "PlayerShooting", fields={
        "projectilePrefab": ref_component(EXPORTS["PlayerProjectile"]["projectile_component"], PREFAB_GUIDS["PlayerProjectile"]),
        "firePoint": ref_component(fp_tr),
    })
    playerhealth_mb = u.monobehaviour(root_go, "PlayerHealth", fields={})

    root_tr = u.transform(root_go, position=(x, y, 0), children=[gc_tr, fp_tr], parent=0)
    fix_parent(u, gc_tr, root_tr)
    fix_parent(u, fp_tr, root_tr)

    u.write_game_object(gc_go, "GroundCheck", tag="Untagged", component_ids=[gc_tr])
    u.write_game_object(fp_go, "FirePoint", tag="Untagged", component_ids=[fp_tr])
    u.write_game_object(root_go, "Player", tag="Player", component_ids=[
        root_tr, sr, rb, col, health_mb, controller_mb, shooting_mb, playerhealth_mb,
    ])
    return {"go": root_go, "transform": root_tr, "health": health_mb}


def add_enemy_melee(u, x, y, active=True, name="EnemyMelee"):
    root_go = u.new_go()
    dz_go = u.new_go()
    dz_tr = u.transform(dz_go, position=(0, 0, 0), parent=None)

    sr = u.sprite_renderer(root_go, "enemy_melee", order=5)
    rb = u.rigidbody2d(root_go, gravity_scale=3, fixed_rotation=True)
    col = u.box_collider2d(root_go, size=(0.42, 0.62))
    dz_col = u.circle_collider2d(dz_go, radius=3.0, is_trigger=True)
    dz_mb = u.monobehaviour(dz_go, "DetectionZone", fields={})
    health_mb = u.monobehaviour(root_go, "Health", fields={"maxHealth": 2})
    enemy_mb = u.monobehaviour(root_go, "EnemyMelee", fields={"detectionZone": ref_component(dz_mb)})

    root_tr = u.transform(root_go, position=(x, y, 0), children=[dz_tr], parent=0)
    fix_parent(u, dz_tr, root_tr)

    u.write_game_object(dz_go, "DetectionZone", tag="Untagged", component_ids=[dz_tr, dz_col, dz_mb])
    u.write_game_object(root_go, name, tag="Enemy",
                         component_ids=[root_tr, sr, rb, col, health_mb, enemy_mb],
                         is_active=(1 if active else 0))
    return root_go


def add_enemy_ranged(u, x, y, active=True, name="EnemyRanged"):
    root_go = u.new_go()
    dz_go = u.new_go()
    fp_go = u.new_go()
    dz_tr = u.transform(dz_go, position=(0, 0, 0), parent=None)
    fp_tr = u.transform(fp_go, position=(0.26, 0.05, 0), parent=None)

    sr = u.sprite_renderer(root_go, "enemy_ranged", order=5)
    rb = u.rigidbody2d(root_go, gravity_scale=3, fixed_rotation=True)
    col = u.box_collider2d(root_go, size=(0.42, 0.62))
    dz_col = u.circle_collider2d(dz_go, radius=5.0, is_trigger=True)
    dz_mb = u.monobehaviour(dz_go, "DetectionZone", fields={})
    health_mb = u.monobehaviour(root_go, "Health", fields={"maxHealth": 2})
    enemy_mb = u.monobehaviour(root_go, "EnemyRanged", fields={
        "detectionZone": ref_component(dz_mb),
        "projectilePrefab": ref_component(EXPORTS["EnemyProjectile"]["projectile_component"], PREFAB_GUIDS["EnemyProjectile"]),
        "firePoint": ref_component(fp_tr),
    })

    root_tr = u.transform(root_go, position=(x, y, 0), children=[dz_tr, fp_tr], parent=0)
    fix_parent(u, dz_tr, root_tr)
    fix_parent(u, fp_tr, root_tr)

    u.write_game_object(dz_go, "DetectionZone", tag="Untagged", component_ids=[dz_tr, dz_col, dz_mb])
    u.write_game_object(fp_go, "FirePoint", tag="Untagged", component_ids=[fp_tr])
    u.write_game_object(root_go, name, tag="Enemy",
                         component_ids=[root_tr, sr, rb, col, health_mb, enemy_mb],
                         is_active=(1 if active else 0))
    return root_go


def add_level_exit(u, x, y, w, h, next_scene, name="LevelExit"):
    go = u.new_go()
    tr = u.transform(go, position=(x, y, 0), parent=0)
    col = u.box_collider2d(go, size=(w, h), is_trigger=True)
    mb = u.monobehaviour(go, "LevelExitTrigger", fields={"nextSceneName": next_scene})
    u.write_game_object(go, name, tag="Untagged", component_ids=[tr, col, mb])
    return go


def add_combat_zone(u, x, y, w, h, enemy_ids, name="CombatZone"):
    go = u.new_go()
    tr = u.transform(go, position=(x, y, 0), parent=0)
    col = u.box_collider2d(go, size=(w, h), is_trigger=True)
    mb = u.monobehaviour(go, "CombatZoneActivator", fields={"enemiesToActivate": list(enemy_ids)})
    u.write_game_object(go, name, tag="Untagged", component_ids=[tr, col, mb])
    return go


def add_pickup(u, x, y, kind, name=None):
    prefab_field = "pickup_health" if kind == "health" else "pickup_ammo"
    go = u.new_go()
    tr = u.transform(go, position=(x, y, 0), parent=0)
    sr = u.sprite_renderer(go, prefab_field, order=4)
    col = u.circle_collider2d(go, radius=0.3, is_trigger=True)
    fields = {} if kind == "health" else {"type": 1, "amount": 10}
    mb = u.monobehaviour(go, "PickupItem", fields=fields)
    u.write_game_object(go, name or f"Pickup_{kind}", tag="Untagged", component_ids=[tr, sr, col, mb])
    return go


def add_camera(u, target_transform_id):
    go = u.new_go()
    tr = u.transform(go, position=(0, 1, -10), parent=0)
    cam = u.camera(go, size=5.5)
    al = u.audio_listener(go)
    follow_mb = u.monobehaviour(go, "CameraFollow", fields={"target": ref_component(target_transform_id)})
    u.write_game_object(go, "Main Camera", tag="Untagged", component_ids=[tr, cam, al, follow_mb])
    return go


def add_manager(u, script_name, name=None):
    go = u.new_go()
    tr = u.transform(go, position=(0, 0, 0), parent=0)
    mb = u.monobehaviour(go, script_name, fields={})
    u.write_game_object(go, name or script_name, tag="Untagged", component_ids=[tr, mb])
    return go


def write_scene(name, unity_file):
    rel_path = f"Assets/Scenes/{name}.unity"
    full_path = os.path.join(ROOT, rel_path)
    g = guid_for(rel_path)
    with open(full_path, "w", newline="\n") as f:
        f.write(unity_file.render())
    with open(full_path + ".meta", "w", newline="\n") as f:
        f.write(SCENE_META.format(guid=g))
    print("scene:", name, g)
    return g


# ---------------------------------------------------------------------------
# LEVEL 01 : plutôt plat, un fossé à sauter, une petite embuscade.
# ---------------------------------------------------------------------------
u = UnityFile()

add_platform_run(u, -9, 2, 0)           # sol principal
add_platform_run(u, 5, 16, 0)           # sol après le fossé (fossé x=3..4)
add_platform_run(u, 9, 11, 1.3)         # plateforme flottante (hauteur atteignable au saut)

player = add_player(u, -8, 1.2)
add_camera(u, player["transform"])
add_manager(u, "GameManager")
add_manager(u, "ScoreManager")

add_enemy_melee(u, -3, 1, active=True, name="EnemyMelee_Patrol")

ambush_a = add_enemy_melee(u, 7, 1, active=False, name="EnemyMelee_Embuscade")
ambush_b = add_enemy_ranged(u, 10, 2.11, active=False, name="EnemyRanged_Embuscade")
add_combat_zone(u, 1.5, 1, 2, 3, [ambush_a, ambush_b], name="CombatZone_Embuscade")

add_pickup(u, 13, 1, "health")
add_level_exit(u, 16.5, 1, 1, 4, "Level02")

SCENE1_GUID = write_scene("Level01", u)

# ---------------------------------------------------------------------------
# LEVEL 02 : progression verticale (plateformes en escalier), plus d'ennemis
# à distance, embuscade différente, boucle vers Level01 à la fin.
# ---------------------------------------------------------------------------
u = UnityFile()

add_platform_run(u, -9, -3, 0)          # zone de départ
add_platform_run(u, -1, 1, 1.2)
add_platform_run(u, 3, 5, 2.4)
add_platform_run(u, 7, 9, 3.6)
add_platform_run(u, 11, 13, 2.4)
add_platform_run(u, 15, 17, 1.2)
add_platform_run(u, 19, 26, 0)          # zone finale
# Paliers de 1.2 unité : atteignables au saut (portée verticale ~1.38 unité).

player = add_player(u, -8, 1.2)
add_camera(u, player["transform"])
add_manager(u, "GameManager")
add_manager(u, "ScoreManager")

add_enemy_ranged(u, 4, 3.21, active=True, name="EnemyRanged_Plateforme")
add_enemy_melee(u, 16, 2.01, active=True, name="EnemyMelee_Final")

ambush_c = add_enemy_ranged(u, 23, 0.81, active=False, name="EnemyRanged_Embuscade")
add_combat_zone(u, 19.5, 1, 2, 3, [ambush_c], name="CombatZone_Embuscade")

add_pickup(u, 8, 4.4, "ammo")
add_level_exit(u, 26.5, 1, 1, 4, "Level01")

SCENE2_GUID = write_scene("Level02", u)

TABLE["scenes"] = {"Level01": SCENE1_GUID, "Level02": SCENE2_GUID}
with open(os.path.join(ROOT, "_guid_table.json"), "w") as f:
    json.dump(TABLE, f, indent=2)

print("OK - scènes générées")
