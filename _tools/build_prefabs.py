#!/usr/bin/env python3
import hashlib
import json
import os
from unity_yaml import UnityFile, ref_component

ROOT = "/home/claude/project/RunAndGun2D"
PREFABS_DIR = os.path.join(ROOT, "Assets", "Prefabs")
os.makedirs(PREFABS_DIR, exist_ok=True)

PREFAB_META = """fileFormatVersion: 2
guid: {guid}
PrefabImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""


def guid_for(path):
    return hashlib.md5(("RunAndGun2D::" + path).encode("utf-8")).hexdigest()


def write_prefab(name, unity_file):
    rel_path = f"Assets/Prefabs/{name}.prefab"
    full_path = os.path.join(ROOT, rel_path)
    g = guid_for(rel_path)
    with open(full_path, "w", newline="\n") as f:
        f.write(unity_file.render())
    with open(full_path + ".meta", "w", newline="\n") as f:
        f.write(PREFAB_META.format(guid=g))
    print("prefab:", name, g)
    return g


PREFAB_GUIDS = {}
EXPORTS = {}  # infos réutilisées entre prefabs (ex: fileID du script Projectile)

# ---------------------------------------------------------------------------
# PlayerProjectile.prefab
# ---------------------------------------------------------------------------
u = UnityFile()
go = u.new_go()
tr = u.transform(go, position=(0, 0, 0), parent=0)
sr = u.sprite_renderer(go, "projectile_player", order=6)
rb = u.rigidbody2d(go, gravity_scale=0, fixed_rotation=True)
col = u.circle_collider2d(go, radius=0.07, is_trigger=True)
mb = u.monobehaviour(go, "Projectile", fields={})
u.write_game_object(go, "PlayerProjectile", tag="Untagged", component_ids=[tr, sr, rb, col, mb])
PREFAB_GUIDS["PlayerProjectile"] = write_prefab("PlayerProjectile", u)
EXPORTS["PlayerProjectile"] = {"projectile_component": mb}

# ---------------------------------------------------------------------------
# EnemyProjectile.prefab
# ---------------------------------------------------------------------------
u = UnityFile()
go = u.new_go()
tr = u.transform(go, position=(0, 0, 0), parent=0)
sr = u.sprite_renderer(go, "projectile_enemy", order=6)
rb = u.rigidbody2d(go, gravity_scale=0, fixed_rotation=True)
col = u.circle_collider2d(go, radius=0.07, is_trigger=True)
mb = u.monobehaviour(go, "Projectile", fields={})
u.write_game_object(go, "EnemyProjectile", tag="Untagged", component_ids=[tr, sr, rb, col, mb])
PREFAB_GUIDS["EnemyProjectile"] = write_prefab("EnemyProjectile", u)
EXPORTS["EnemyProjectile"] = {"projectile_component": mb}

# ---------------------------------------------------------------------------
# Player.prefab
# ---------------------------------------------------------------------------
u = UnityFile()
root_go = u.new_go()
gc_go = u.new_go()
fp_go = u.new_go()

gc_tr = u.transform(gc_go, position=(0, -0.34, 0), parent=None)
fp_tr = u.transform(fp_go, position=(0.26, 0.05, 0), parent=None)

sr = u.sprite_renderer(root_go, "player", order=5)
rb = u.rigidbody2d(root_go, gravity_scale=3, fixed_rotation=True)
col = u.box_collider2d(root_go, size=(0.42, 0.62), offset=(0, 0))
health_mb = u.monobehaviour(root_go, "Health", fields={"maxHealth": 5})
controller_mb = u.monobehaviour(root_go, "PlayerController", fields={
    "groundCheck": ref_component(gc_tr),
})
shooting_mb = u.monobehaviour(root_go, "PlayerShooting", fields={
    "projectilePrefab": ref_component(EXPORTS["PlayerProjectile"]["projectile_component"], PREFAB_GUIDS["PlayerProjectile"]),
    "firePoint": ref_component(fp_tr),
})
playerhealth_mb = u.monobehaviour(root_go, "PlayerHealth", fields={})

root_tr = u.transform(root_go, position=(-6, 0, 0), children=[gc_tr, fp_tr], parent=0)

# On complète maintenant le m_Father des enfants (le root_tr n'était pas encore connu).
def fix_parent(unity_file, transform_id, new_parent_id):
    marker = f"--- !u!4 &{transform_id}\n"
    for i, block in enumerate(unity_file.blocks):
        if block.startswith(marker):
            unity_file.blocks[i] = block.replace("m_Father: {fileID: 0}", f"m_Father: {{fileID: {new_parent_id}}}", 1)
            return
    raise RuntimeError(f"transform {transform_id} introuvable")


fix_parent(u, gc_tr, root_tr)
fix_parent(u, fp_tr, root_tr)

u.write_game_object(gc_go, "GroundCheck", tag="Untagged", component_ids=[gc_tr])
u.write_game_object(fp_go, "FirePoint", tag="Untagged", component_ids=[fp_tr])
u.write_game_object(root_go, "Player", tag="Player", component_ids=[
    root_tr, sr, rb, col, health_mb, controller_mb, shooting_mb, playerhealth_mb,
])

PREFAB_GUIDS["Player"] = write_prefab("Player", u)

# ---------------------------------------------------------------------------
# EnemyMelee.prefab
# ---------------------------------------------------------------------------
u = UnityFile()
root_go = u.new_go()
dz_go = u.new_go()
dz_tr = u.transform(dz_go, position=(0, 0, 0), parent=None)

sr = u.sprite_renderer(root_go, "enemy_melee", order=5)
rb = u.rigidbody2d(root_go, gravity_scale=3, fixed_rotation=True)
col = u.box_collider2d(root_go, size=(0.42, 0.62), offset=(0, 0))
dz_col = u.circle_collider2d(dz_go, radius=3.0, is_trigger=True)
dz_mb = u.monobehaviour(dz_go, "DetectionZone", fields={})
health_mb = u.monobehaviour(root_go, "Health", fields={"maxHealth": 2})
enemy_mb = u.monobehaviour(root_go, "EnemyMelee", fields={
    "detectionZone": ref_component(dz_mb),
})

root_tr = u.transform(root_go, position=(2, 0, 0), children=[dz_tr], parent=0)
fix_parent(u, dz_tr, root_tr)

u.write_game_object(dz_go, "DetectionZone", tag="Untagged", component_ids=[dz_tr, dz_col, dz_mb])
u.write_game_object(root_go, "EnemyMelee", tag="Enemy", component_ids=[
    root_tr, sr, rb, col, health_mb, enemy_mb,
])

PREFAB_GUIDS["EnemyMelee"] = write_prefab("EnemyMelee", u)

# ---------------------------------------------------------------------------
# EnemyRanged.prefab
# ---------------------------------------------------------------------------
u = UnityFile()
root_go = u.new_go()
dz_go = u.new_go()
fp_go = u.new_go()
dz_tr = u.transform(dz_go, position=(0, 0, 0), parent=None)
fp_tr = u.transform(fp_go, position=(0.26, 0.05, 0), parent=None)

sr = u.sprite_renderer(root_go, "enemy_ranged", order=5)
rb = u.rigidbody2d(root_go, gravity_scale=3, fixed_rotation=True)
col = u.box_collider2d(root_go, size=(0.42, 0.62), offset=(0, 0))
dz_col = u.circle_collider2d(dz_go, radius=5.0, is_trigger=True)
dz_mb = u.monobehaviour(dz_go, "DetectionZone", fields={})
health_mb = u.monobehaviour(root_go, "Health", fields={"maxHealth": 2})
enemy_mb = u.monobehaviour(root_go, "EnemyRanged", fields={
    "detectionZone": ref_component(dz_mb),
    "projectilePrefab": ref_component(EXPORTS["EnemyProjectile"]["projectile_component"], PREFAB_GUIDS["EnemyProjectile"]),
    "firePoint": ref_component(fp_tr),
})

root_tr = u.transform(root_go, position=(4, 0, 0), children=[dz_tr, fp_tr], parent=0)
fix_parent(u, dz_tr, root_tr)
fix_parent(u, fp_tr, root_tr)

u.write_game_object(dz_go, "DetectionZone", tag="Untagged", component_ids=[dz_tr, dz_col, dz_mb])
u.write_game_object(fp_go, "FirePoint", tag="Untagged", component_ids=[fp_tr])
u.write_game_object(root_go, "EnemyRanged", tag="Enemy", component_ids=[
    root_tr, sr, rb, col, health_mb, enemy_mb,
])

PREFAB_GUIDS["EnemyRanged"] = write_prefab("EnemyRanged", u)

# ---------------------------------------------------------------------------
# Platform.prefab (pas de script, pas de Rigidbody2D => collider statique)
# ---------------------------------------------------------------------------
u = UnityFile()
go = u.new_go()
tr = u.transform(go, position=(0, 0, 0), parent=0)
sr = u.sprite_renderer(go, "platform", order=0)
col = u.box_collider2d(go, size=(1, 1))
u.write_game_object(go, "Platform", tag="Ground", component_ids=[tr, sr, col])
PREFAB_GUIDS["Platform"] = write_prefab("Platform", u)

# ---------------------------------------------------------------------------
# HealthPickup.prefab / AmmoPickup.prefab
# ---------------------------------------------------------------------------
u = UnityFile()
go = u.new_go()
tr = u.transform(go, position=(0, 0, 0), parent=0)
sr = u.sprite_renderer(go, "pickup_health", order=4)
col = u.circle_collider2d(go, radius=0.3, is_trigger=True)
mb = u.monobehaviour(go, "PickupItem", fields={})
u.write_game_object(go, "HealthPickup", tag="Untagged", component_ids=[tr, sr, col, mb])
PREFAB_GUIDS["HealthPickup"] = write_prefab("HealthPickup", u)

u = UnityFile()
go = u.new_go()
tr = u.transform(go, position=(0, 0, 0), parent=0)
sr = u.sprite_renderer(go, "pickup_ammo", order=4)
col = u.circle_collider2d(go, radius=0.3, is_trigger=True)
mb = u.monobehaviour(go, "PickupItem", fields={"type": 1, "amount": 10})
u.write_game_object(go, "AmmoPickup", tag="Untagged", component_ids=[tr, sr, col, mb])
PREFAB_GUIDS["AmmoPickup"] = write_prefab("AmmoPickup", u)

# ---------------------------------------------------------------------------
with open(os.path.join(ROOT, "_guid_table.json")) as f:
    table = json.load(f)
table["prefabs"] = PREFAB_GUIDS
table["exports"] = EXPORTS
with open(os.path.join(ROOT, "_guid_table.json"), "w") as f:
    json.dump(table, f, indent=2)

print("OK - prefabs générés")
