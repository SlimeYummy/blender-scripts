#
# 旋转骨骼并写入fcurve
# 支持blender view视图中的多种旋转模式
#

import bpy
import math
from action_utils import find_fcurve_by_id, new_fcurve

ROT_AXIS = 'X'
ROT_TYPE = 'GLOBAL'
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


def apply_rot(frame, rot):
    selected_bones = [bone for bone in obj.pose.bones if bone.select]

    if not selected_bones:
        print("No bones selected")
        return

    bpy.ops.transform.rotate(
        value=math.radians(rot),
        orient_axis=ROT_AXIS,
        orient_type=ROT_TYPE
    )

    for bone in selected_bones:
        path = None
        if bone.rotation_mode == 'QUATERNION':
            path = "rotation_quaternion"
        elif bone.rotation_mode == 'AXIS_ANGLE':
            path = "rotation_axis_angle"
        else:
            path = "rotation_euler"

        bone.keyframe_insert(data_path=path, frame=frame, group=bone.name)


def by_fcurve():
    fcurve = None
    if ROT_AXIS == 'X':
        fcurve = find_fcurve_by_id(active_action, 'Rot.x')
        if not fcurve:
            fcurve = new_fcurve(active_action, active_bone.name, 'Rot', 0)
    elif ROT_AXIS == 'Y':
        fcurve = find_fcurve_by_id(active_action, 'Rot.y')
        if not fcurve:
            fcurve = new_fcurve(active_action, active_bone.name, 'Rot', 1)
    elif ROT_AXIS == 'Z':
        fcurve = find_fcurve_by_id(active_action, 'Rot.z')
        if not fcurve:
            fcurve = new_fcurve(active_action, active_bone.name, 'Rot', 2)

    for frame in FRAMES:
        bpy.context.scene.frame_set(frame)

        rot = fcurve.evaluate(frame)
        print(f'frame: {frame}, rot: {rot}')
        if abs(rot) < 1e-5:
            continue

        apply_rot(frame, rot)


by_fcurve()
# apply_rot(0, -10)
