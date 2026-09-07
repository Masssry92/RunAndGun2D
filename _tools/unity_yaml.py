"""
Petit "DSL" pour générer des fichiers .prefab / .unity Unity valides à la main,
avec des GameObjects + composants standards (Transform, SpriteRenderer,
Rigidbody2D, BoxCollider2D, CircleCollider2D, MonoBehaviour).

Règle importante : pour un MonoBehaviour, on n'écrit que les champs dont la
valeur doit différer du défaut du script (Unity construit l'objet via le
constructeur C# -- donc applique les initialiseurs de champs -- puis surcharge
uniquement les champs présents dans le YAML).
"""
import json
import os

ROOT = "/home/claude/project/RunAndGun2D"

with open(os.path.join(ROOT, "_guid_table.json")) as f:
    GUIDS = json.load(f)

SCRIPT_GUIDS = GUIDS["scripts"]
SPRITE_GUIDS = GUIDS["sprites"]

HEADER = """%YAML 1.1
%TAG !u! tag:unity3d.com:
"""

SPRITE_DEFAULT_MATERIAL = "{fileID: 10754, guid: 0000000000000000f000000000000000, type: 0}"


class IdAllocator:
    """Alloue des fileID uniques et croissants pour un fichier donné."""

    def __init__(self, start=1000000):
        self._next = start

    def new(self):
        v = self._next
        self._next += 1
        return v


class UnityFile:
    """Représente un fichier .unity ou .prefab en cours de construction."""

    def __init__(self):
        self.ids = IdAllocator()
        self.blocks = []  # liste de strings YAML, un par objet

    def add_block(self, class_id, obj_id, body):
        self.blocks.append(f"--- !u!{class_id} &{obj_id}\n{body}")

    def render(self):
        return HEADER + "".join(self.blocks)

    # -- primitives ----------------------------------------------------
    def new_go(self):
        """Réserve un fileID de GameObject SANS écrire le bloc (le bloc final,
        avec la liste complète des composants, doit être écrit en dernier via
        write_game_object, une fois tous les composants créés)."""
        return self.ids.new()

    def write_game_object(self, gid, name, tag="Untagged", layer=0, component_ids=None, is_active=1):
        comps = "\n".join(f"  - component: {{fileID: {cid}}}" for cid in (component_ids or []))
        body = f"""GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
{comps}
  m_Layer: {layer}
  m_Name: {name}
  m_TagString: {tag}
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: {is_active}
"""
        self.add_block(1, gid, body)
        return gid

    def transform(self, go_id, position=(0, 0, 0), children=None, parent=0, scale=(1, 1, 1)):
        if parent is None:
            parent = 0  # placeholder ; à corriger ensuite avec fix_parent() une fois le parent connu
        tid = self.ids.new()
        child_lines = "\n".join(f"  - {{fileID: {c}}}" for c in (children or []))
        children_block = "  m_Children:\n" + child_lines + "\n" if children else "  m_Children: []\n"
        body = f"""Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: {position[0]}, y: {position[1]}, z: {position[2] if len(position) > 2 else 0}}}
  m_LocalScale: {{x: {scale[0]}, y: {scale[1]}, z: {scale[2] if len(scale) > 2 else 1}}}
  m_ConstrainProportionsScale: 0
{children_block}  m_Father: {{fileID: {parent}}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
"""
        self.add_block(4, tid, body)
        return tid

    def sprite_renderer(self, go_id, sprite_name, order=0, color=(1, 1, 1, 1)):
        sid = self.ids.new()
        sprite_guid = SPRITE_GUIDS[sprite_name]
        r, g, b, a = color
        body = f"""SpriteRenderer:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_Enabled: 1
  m_CastShadows: 0
  m_ReceiveShadows: 0
  m_DynamicOccludee: 1
  m_StaticShadowCaster: 0
  m_MotionVectors: 1
  m_LightProbeUsage: 1
  m_ReflectionProbeUsage: 1
  m_RayTracingMode: 0
  m_RayTraceProcedural: 0
  m_RenderingLayerMask: 1
  m_RendererPriority: 0
  m_Materials:
  - {SPRITE_DEFAULT_MATERIAL}
  m_StaticBatchInfo:
    firstSubMesh: 0
    subMeshCount: 0
  m_StaticBatchRoot: {{fileID: 0}}
  m_ProbeAnchor: {{fileID: 0}}
  m_LightProbeVolumeOverride: {{fileID: 0}}
  m_ScaleInLightmap: 1
  m_ReceiveGI: 1
  m_PreserveUVs: 0
  m_IgnoreNormalsForChartDetection: 0
  m_ImportantGI: 0
  m_StitchLightmapSeams: 1
  m_SelectedEditorRenderState: 0
  m_MinimumChartSize: 4
  m_AutoUVMaxDistance: 0.5
  m_AutoUVMaxAngle: 89
  m_LightmapParameters: {{fileID: 0}}
  m_SortingLayerID: 0
  m_SortingLayer: 0
  m_SortingOrder: {order}
  m_Sprite: {{fileID: 21300000, guid: {sprite_guid}, type: 3}}
  m_Color: {{r: {r}, g: {g}, b: {b}, a: {a}}}
  m_FlipX: 0
  m_FlipY: 0
  m_DrawMode: 0
  m_Size: {{x: 1, y: 1}}
  m_AdaptiveModeThreshold: 0.5
  m_SpriteTileMode: 0
  m_WasSpriteAssigned: 1
  m_MaskInteraction: 0
  m_SpriteSortPoint: 0
"""
        self.add_block(212, sid, body)
        return sid

    def rigidbody2d(self, go_id, body_type=0, gravity_scale=1, fixed_rotation=True, mass=1):
        rid = self.ids.new()
        constraints = 4 if fixed_rotation else 0
        body = f"""Rigidbody2D:
  serializedVersion: 4
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_BodyType: {body_type}
  m_Simulated: 1
  m_UseFullKinematicContacts: 0
  m_UseAutoMass: 0
  m_Mass: {mass}
  m_LinearDrag: 0
  m_AngularDrag: 0.05
  m_GravityScale: {gravity_scale}
  m_Material: {{fileID: 0}}
  m_Constraints: {constraints}
  m_CollideConnected: 0
"""
        self.add_block(50, rid, body)
        return rid

    def box_collider2d(self, go_id, size=(1, 1), offset=(0, 0), is_trigger=False):
        cid = self.ids.new()
        body = f"""BoxCollider2D:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_Enabled: 1
  serializedVersion: 3
  m_Density: 1
  m_Material: {{fileID: 0}}
  m_IsTrigger: {1 if is_trigger else 0}
  m_UsedByEffector: 0
  m_UsedByComposite: 0
  m_Offset: {{x: {offset[0]}, y: {offset[1]}}}
  m_SpriteTilingProperty:
    border: {{x: 0, y: 0, z: 0, w: 0}}
    pivot: {{x: 0.5, y: 0.5}}
    oldSize: {{x: 1, y: 1}}
    newSize: {{x: 1, y: 1}}
    adaptiveTilingThreshold: 0.5
    drawMode: 0
    adaptiveTiling: 0
  m_AutoTiling: 0
  m_Size: {{x: {size[0]}, y: {size[1]}}}
  m_EdgeRadius: 0
"""
        self.add_block(61, cid, body)
        return cid

    def circle_collider2d(self, go_id, radius=0.5, offset=(0, 0), is_trigger=False):
        cid = self.ids.new()
        body = f"""CircleCollider2D:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_Enabled: 1
  serializedVersion: 2
  m_Density: 1
  m_Material: {{fileID: 0}}
  m_IsTrigger: {1 if is_trigger else 0}
  m_UsedByEffector: 0
  m_Offset: {{x: {offset[0]}, y: {offset[1]}}}
  m_Radius: {radius}
"""
        self.add_block(58, cid, body)
        return cid

    def monobehaviour(self, go_id, script_name, fields=None):
        mid = self.ids.new()
        script_guid = SCRIPT_GUIDS[script_name]
        field_lines = ""
        for k, v in (fields or {}).items():
            if isinstance(v, list):
                # Tableau de références (ex: GameObject[]) -> séquence YAML au même niveau que la clé.
                if not v:
                    field_lines += f"  {k}: []\n"
                else:
                    field_lines += f"  {k}:\n"
                    for item in v:
                        field_lines += f"  - {{fileID: {item}}}\n"
            else:
                field_lines += f"  {k}: {v}\n"
        body = f"""MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 11500000, guid: {script_guid}, type: 3}}
  m_Name:
  m_EditorClassIdentifier:
{field_lines}"""
        self.add_block(114, mid, body)
        return mid

    def camera(self, go_id, size=5, bg=(0.15, 0.15, 0.18, 1), depth=-1):
        cid = self.ids.new()
        r, g, b, a = bg
        body = f"""Camera:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_Enabled: 1
  serializedVersion: 2
  m_ClearFlags: 1
  m_BackGroundColor: {{r: {r}, g: {g}, b: {b}, a: {a}}}
  m_projectionMatrixMode: 1
  m_GateFitMode: 2
  m_FOVAxisMode: 0
  m_Iso: 200
  m_ShutterSpeed: 0.005
  m_Aperture: 16
  m_FocusDistance: 10
  m_SensorSize: {{x: 36, y: 24}}
  m_LensShift: {{x: 0, y: 0}}
  m_FocalLength: 50
  m_NormalizedViewPortRect:
    serializedVersion: 2
    x: 0
    y: 0
    width: 1
    height: 1
  near clip plane: 0.3
  far clip plane: 1000
  field of view: 60
  orthographic: 1
  orthographic size: {size}
  m_Depth: {depth}
  m_CullingMask:
    serializedVersion: 2
    m_Bits: 4294967295
  m_RenderingPath: -1
  m_TargetTexture: {{fileID: 0}}
  m_TargetDisplay: 0
  m_TargetEye: 3
  m_HDR: 1
  m_AllowMSAA: 1
  m_AllowDynamicResolution: 0
  m_ForceIntoRT: 0
  m_OcclusionCulling: 1
  m_StereoConvergence: 10
  m_StereoSeparation: 0.022
"""
        self.add_block(20, cid, body)
        return cid

    def audio_listener(self, go_id):
        aid = self.ids.new()
        body = f"""AudioListener:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_Enabled: 1
"""
        self.add_block(81, aid, body)
        return aid


def ref_component(file_id, guid=None):
    """Référence vers un composant : interne (même fichier) ou externe (autre asset)."""
    if guid is None:
        return f"{{fileID: {file_id}}}"
    return f"{{fileID: {file_id}, guid: {guid}, type: 3}}"
