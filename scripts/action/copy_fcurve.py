import bpy
from action_utils import action_frame_range


class CopyMeta:
    from_action: str
    from_bone: str
    to_action: str
    to_bone: str
    mapping: dict[str, str]

    def __init__(self, from_action, from_bone, to_action, to_bone, mapping=None):
        self.from_action = from_action
        self.from_bone = from_bone
        self.to_action = to_action
        self.to_bone = to_bone
        self.mapping = mapping if mapping is not None else { 'x': '-x', 'y': 'z', 'z': 'y' }


CFG_METAS = [
    CopyMeta('Hit1_Empty_B#edit2', 'c_pos', 'Hit1_Empty_B', 'Root'),
    CopyMeta('Hit1_Empty_F#edit2', 'c_pos', 'Hit1_Empty_F', 'Root'),
    CopyMeta('Hit1_Empty_L#edit2', 'c_pos', 'Hit1_Empty_L', 'Root'),
    CopyMeta('Hit1_Empty_R#edit2', 'c_pos', 'Hit1_Empty_R', 'Root'),
]

AXIS_INDEX = { 'x': 0, 'y': 1, 'z': 2, '-x': 0, '-y': 1, '-z': 2 }

print('====================================')

obj = bpy.context.view_layer.objects.active
if not obj or not obj.animation_data or not obj.animation_data.action:
    raise Exception('No active action')

current_action = obj.animation_data.action
meta = next((m for m in CFG_METAS if m.from_action == current_action.name), None)
if meta is None:
    raise Exception(f'No meta found for action "{current_action.name}"')

from_action = bpy.data.actions.get(meta.from_action)
if not from_action:
    raise Exception(f'from_action "{meta.from_action}" not found')

to_action = bpy.data.actions.get(meta.to_action)
if not to_action:
    raise Exception(f'to_action "{meta.to_action}" not found')

# Prepare target fcurves in to_action
to_bone_path = f'pose.bones["{meta.to_bone}"].location'
to_fcurves: dict[str, bpy.types.FCurve] = {}
for to_axis in set(meta.mapping.values()):
    idx = AXIS_INDEX[to_axis]
    fc = to_action.fcurves.find(to_bone_path, index=idx)
    if fc is None:
        fc = to_action.fcurves.new(to_bone_path, index=idx)
    fc.keyframe_points.clear()
    to_fcurves[to_axis] = fc

# Sample from_bone location for every frame in from_action
saved_frame = bpy.context.scene.frame_current
obj.animation_data.action = from_action

frame_range = action_frame_range(from_action)
collected: dict[str, list[tuple[int, float]]] = { axis: [] for axis in meta.mapping }

try:
    for frame in frame_range:
        bpy.context.scene.frame_set(frame)
        pose_bone = obj.pose.bones.get(meta.from_bone)
        if pose_bone is None:
            raise Exception(f'Bone "{meta.from_bone}" not found on object "{obj.name}"')
        loc = pose_bone.location
        for from_axis in meta.mapping:
            collected[from_axis].append((frame, loc[AXIS_INDEX[from_axis]]))
finally:
    bpy.context.scene.frame_set(saved_frame)

# Write collected data into to_action fcurves
for from_axis, to_axis in meta.mapping.items():
    fc = to_fcurves[to_axis]
    for frame, value in collected[from_axis]:
        sign = -1.0 if to_axis.startswith('-') else 1.0
        kf = fc.keyframe_points.insert(frame, value * sign, options={'FAST'})
        kf.interpolation = 'LINEAR'
    fc.update()

print(
    f'Copied {len(frame_range)} frames: '
    f'"{meta.from_action}" / "{meta.from_bone}" -> '
    f'"{meta.to_action}" / "{meta.to_bone}"'
)
