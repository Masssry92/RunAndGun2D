#!/usr/bin/env python3
"""
Générateur du projet Unity RunAndGun2D : .meta (scripts + sprites), Prefabs,
Scènes, ProjectSettings minimaux et Packages/manifest.json.

Approche : on sérialise uniquement les GameObjects/Components utiles, et pour
chaque MonoBehaviour on n'écrit QUE les champs dont la valeur diffère du
défaut du script (Unity construit l'objet C# -- donc exécute les
initialiseurs de champs -- puis applique par-dessus les champs présents dans
le YAML ; les champs absents gardent leur valeur par défaut C#).
"""
import hashlib
import os

ROOT = "/home/claude/project/RunAndGun2D"
ASSETS = os.path.join(ROOT, "Assets")


def guid_for(path):
    """GUID déterministe (32 hex) à partir d'un chemin relatif stable."""
    h = hashlib.md5(("RunAndGun2D::" + path).encode("utf-8")).hexdigest()
    return h


# ---------------------------------------------------------------------------
# .meta pour les scripts C#
# ---------------------------------------------------------------------------
SCRIPT_META_TEMPLATE = """fileFormatVersion: 2
guid: {guid}
MonoImporter:
  externalObjects: {{}}
  serializedVersion: 2
  defaultReferences: []
  executionOrder: 0
  icon: {{instanceID: 0}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""

# ---------------------------------------------------------------------------
# .meta pour les sprites PNG
# ---------------------------------------------------------------------------
SPRITE_META_TEMPLATE = """fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 12
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 0
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: {ppu}
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  applyGammaDecoding: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID:
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  spritePackingTag:
  pSDRemoveMatte: 0
  pSDShowRemoveMatteOption: 0
  userData:
  assetBundleName:
  assetBundleVariant:
"""


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        f.write(content)


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


# --- 1. Scripts : un .meta par .cs -----------------------------------------
SCRIPT_GUIDS = {}
for dirpath, _, filenames in os.walk(os.path.join(ASSETS, "Scripts")):
    for fn in sorted(filenames):
        if fn.endswith(".cs"):
            full = os.path.join(dirpath, fn)
            r = rel(full)
            g = guid_for(r)
            SCRIPT_GUIDS[fn[:-3]] = g  # clé = nom de classe (== nom de fichier)
            write(full + ".meta", SCRIPT_META_TEMPLATE.format(guid=g))

print("Scripts:", len(SCRIPT_GUIDS))
for k, v in SCRIPT_GUIDS.items():
    print(" ", k, v)

# --- 2. Sprites : un .meta par .png -----------------------------------------
SPRITE_GUIDS = {}
for folder in ["Sprites", "UI"]:
    d = os.path.join(ASSETS, folder)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".png"):
            full = os.path.join(d, fn)
            r = rel(full)
            g = guid_for(r)
            SPRITE_GUIDS[fn[:-4]] = g
            write(full + ".meta", SPRITE_META_TEMPLATE.format(guid=g, ppu=100))

print("Sprites:", len(SPRITE_GUIDS))
for k, v in SPRITE_GUIDS.items():
    print(" ", k, v)

# Sauvegarde des tables de GUID pour les étapes suivantes (prefabs/scenes)
import json
with open(os.path.join(ROOT, "_guid_table.json"), "w") as f:
    json.dump({"scripts": SCRIPT_GUIDS, "sprites": SPRITE_GUIDS}, f, indent=2)

print("OK - metas écrits")
