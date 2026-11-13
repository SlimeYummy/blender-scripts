#
# 平移骨骼并写入fcurve
# 支持blender view视图中的多种平移模式
#

import bpy
import math
from action_utils import find_fcurve_by_id, new_fcurve

TRANS_TYPE = 'GLOBAL'
TRANS_AXIS = 'Y'
FRAMES = range(0, 57)

obj = bpy.context.active_object
if obj is None or obj.type != 'ARMATURE':
    raise Exception('No armature object selected')
if obj.mode != 'POSE':
    raise Exception('Must be in pose mode')

if not obj.animation_data or not obj.animation_data.action:
    raise Exception('No active action found')
active_action = obj.animation_data.action

active_bone = bpy.context.active_pose_bone
if active_bone is None:
    raise Exception('No active bone selected')


def apply_trans(frame, trans):
    selected_bones = [bone for bone in obj.pose.bones if bone.select]
    
    if not selected_bones:
        print("No bones selected")
        return

    bpy.ops.transform.translate(
        value=(trans if TRANS_AXIS == 'X' else 0,
               trans if TRANS_AXIS == 'Y' else 0,
               trans if TRANS_AXIS == 'Z' else 0),
        orient_type=TRANS_TYPE
    )

    path = "location"
    for bone in selected_bones:
        bone.keyframe_insert(data_path=path, frame=frame, group=bone.name)


def by_fcurve():
    fcurve = None
    if TRANS_AXIS == 'X':
        fcurve = find_fcurve_by_id(active_action, 'Loc.x')
        if not fcurve:
            fcurve = new_fcurve(active_action, active_bone.name, 'Loc', 0)
    elif TRANS_AXIS == 'Y':
        fcurve = find_fcurve_by_id(active_action, 'Loc.y')
        if not fcurve:
            fcurve = new_fcurve(active_action, active_bone.name, 'Loc', 1)
    elif TRANS_AXIS == 'Z':
        fcurve = find_fcurve_by_id(active_action, 'Loc.z')
        if not fcurve:
            fcurve = new_fcurve(active_action, active_bone.name, 'Loc', 2)

    for frame in FRAMES:
        bpy.context.scene.frame_set(frame)

        trans = fcurve.evaluate(frame)
        print(f'frame: {frame}, trans: {trans}')
        if abs(trans) < 1e-5:
            continue
        
        apply_trans(frame, trans)


by_fcurve()
# apply_trans(0, 1.0)
