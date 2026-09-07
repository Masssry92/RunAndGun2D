#!/usr/bin/env python3
"""Vérifie la cohérence interne des .prefab/.unity générés :
- chaque référence interne {fileID: X} (sans guid) pointe vers une ancre existante du même fichier
- chaque référence externe {fileID: X, guid: G} pointe vers un guid connu (script, sprite, prefab)
- chaque composant listé dans m_Component d'un GameObject existe bien et pointe vers ce GameObject
"""
import glob
import json
import os
import re

ROOT = "/home/claude/project/RunAndGun2D"

with open(os.path.join(ROOT, "_guid_table.json")) as f:
    TABLE = json.load(f)

KNOWN_GUIDS = set(TABLE["scripts"].values()) | set(TABLE["sprites"].values()) | set(TABLE["prefabs"].values())
KNOWN_GUIDS.add("0000000000000000f000000000000000")  # matériau Sprites-Default intégré à Unity

ANCHOR_RE = re.compile(r"^--- !u!(\d+) &(-?\d+)")
REF_RE = re.compile(r"\{fileID:\s*(-?\d+)(?:,\s*guid:\s*([0-9a-fA-F]{32}))?[^}]*\}")
GAMEOBJECT_FIELD_RE = re.compile(r"m_GameObject:\s*\{fileID:\s*(-?\d+)\}")

errors = []
warnings = []
files_checked = 0

targets = glob.glob(os.path.join(ROOT, "Assets", "**", "*.prefab"), recursive=True) + \
          glob.glob(os.path.join(ROOT, "Assets", "**", "*.unity"), recursive=True)

for path in sorted(targets):
    files_checked += 1
    rel = os.path.relpath(path, ROOT)
    with open(path) as f:
        content = f.read()

    # 1. anchors : {classID: [fileIDs]}
    anchors = set()
    go_components = {}  # go fileID -> liste des component fileIDs déclarés
    class_of = {}
    blocks = content.split("--- !u!")
    for raw in blocks[1:]:
        block = "--- !u!" + raw
        m = ANCHOR_RE.match(block)
        if not m:
            errors.append(f"{rel}: bloc sans ancre valide : {block[:60]!r}")
            continue
        cls, fid = int(m.group(1)), int(m.group(2))
        if fid in anchors:
            errors.append(f"{rel}: fileID dupliqué {fid}")
        anchors.add(fid)
        class_of[fid] = cls

        if cls == 1:  # GameObject
            comp_ids = [int(x) for x in re.findall(r"- component: \{fileID: (-?\d+)\}", block)]
            go_components[fid] = comp_ids

    # 2. toutes les références (fileID [+ guid]) du fichier
    for m in REF_RE.finditer(content):
        fid = int(m.group(1))
        guid = m.group(2)
        if fid == 0:
            continue  # référence nulle, toujours valide
        if guid:
            if guid not in KNOWN_GUIDS:
                errors.append(f"{rel}: guid externe inconnu {guid} (fileID {fid})")
        else:
            if fid not in anchors:
                errors.append(f"{rel}: référence interne vers fileID {fid} introuvable dans ce fichier")

    # 3. cohérence GameObject <-> composants
    for go_id, comp_ids in go_components.items():
        for cid in comp_ids:
            if cid not in anchors:
                errors.append(f"{rel}: GameObject {go_id} référence le composant {cid} qui n'existe pas")

    # chaque composant (hors GameObject) doit avoir un m_GameObject pointant vers un GO déclaré
    comp_blocks = re.split(r"(?=^--- !u!)", content, flags=re.M)
    for block in comp_blocks:
        m = ANCHOR_RE.match(block)
        if not m:
            continue
        cls, fid = int(m.group(1)), int(m.group(2))
        if cls == 1:
            continue
        gm = GAMEOBJECT_FIELD_RE.search(block)
        if gm:
            go_ref = int(gm.group(1))
            if go_ref not in go_components:
                errors.append(f"{rel}: composant {fid} (classe {cls}) référence un GameObject {go_ref} introuvable")
            elif fid not in go_components[go_ref]:
                warnings.append(f"{rel}: composant {fid} (classe {cls}) n'est pas listé dans m_Component de son GameObject {go_ref}")

print(f"Fichiers vérifiés : {files_checked}")
print(f"Erreurs : {len(errors)}")
for e in errors:
    print("  ERREUR:", e)
print(f"Avertissements : {len(warnings)}")
for w in warnings:
    print("  ATTENTION:", w)

if not errors:
    print("\n✅ Aucune erreur de cohérence détectée.")
else:
    print("\n❌ Des erreurs ont été détectées, voir ci-dessus.")
