import bpy
from action_utils import make_fcurve_id


cfg_target_action = 'Attack_04A_#edit1'

cfg_frame_range = [0, 75]


print('====================================')

selected_bones = bpy.context.selected_pose_bones
if not selected_bones or len(selected_bones) == 0:
    raise Exception('No hands selected')

action = bpy.data.actions.get(cfg_target_action)
if not action:
    raise Exception(f'Action "{cfg_target_action}" not found')

fcurves = {}
for bone in selected_bones:
    for fcurve in action.fcurves:
        if fcurve.data_path.startswith(f'pose.bones["{bone.name}"].'):
            fcurves[make_fcurve_id(fcurve)] = fcurve
            fcurve.keyframe_points.clear()

saved_frame = bpy.context.scene.frame_current
for frame in range(cfg_frame_range[0], cfg_frame_range[1] + 1):
    bpy.context.scene.frame_set(frame)
    for bone in selected_bones:
        tx = fcurves.get(f'pose.bones["{bone.name}"].location.x')
        if tx:
            tx.keyframe_points.insert(frame, bone.location.x, options={'FAST'})
        ty = fcurves.get(f'pose.bones["{bone.name}"].location.y')
        if ty:
            ty.keyframe_points.insert(frame, bone.location.y, options={'FAST'})
        tz = fcurves.get(f'pose.bones["{bone.name}"].location.z')
        if tz:
            tz.keyframe_points.insert(frame, bone.location.z, options={'FAST'})
bpy.context.scene.frame_set(saved_frame)
