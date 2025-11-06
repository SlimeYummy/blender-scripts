import bpy
import importlib
import custom_utils as cu

importlib.reload(cu)


action = bpy.context.active_object.animation_data.action

meta = cu.find_action_meta(action.name)
print(meta.frame_map)


for fcurve in action.fcurves:
    for keyframe in fcurve.keyframe_points:
        raw_frame = int(keyframe.co[0])
        if raw_frame not in meta.frame_map:
            fcurve.keyframe_points.remove(keyframe, fast=True)

    for keyframe in fcurve.keyframe_points:
        raw_frame = int(keyframe.co[0])
        frame = meta.frame_map[raw_frame]
        keyframe.co[0] = meta.frame_map[raw_frame]
