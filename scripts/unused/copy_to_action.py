import math
import bpy
from mathutils import Vector, Euler, Quaternion
from action_utils import travel_action_fcurves

dst_action_name = 'AttackAxe_1_1_edit'

start_frame = 0
finish_frame = 108

init_pos = Vector((0, 0, 0))
init_rot = Quaternion((1, 0, 0, 0))
# init_rot = Euler((0, -math.pi / 2, 0), 'XYZ').to_quaternion()


if not bpy.context.active_object:
    raise Exception('No armature selected')
src_obj = bpy.context.active_object

action = bpy.data.actions.get(dst_action_name)
if not action:
    raise Exception(f'Action "{action}" not found')
if not action.fcurves or len(action.fcurves) != 6:
    raise Exception(f'Action "{action}" must have 6 fcurves')
for fcurve in action.fcurves:
    fcurve.keyframe_points.clear()

# start_frame = 0
# finish_frame = 0
# def visitor(fcurve):
#     if ik_joint1 in fcurve.data_path or ik_joint2 in fcurve.data_path:
#         global start_frame, finish_frame
#         start_frame = min(start_frame, fcurve.keyframe_points[0].co[0])
#         finish_frame = max(finish_frame, fcurve.keyframe_points[-1].co[0])
# travel_action_fcurves(None, visitor, location=True)

saved_frame = bpy.context.scene.frame_current
for frame in range(start_frame, finish_frame + 1):
    bpy.context.scene.frame_set(frame)

#     pose_bone1 = armature.pose.bones.get(ik_joint1)
#     if not pose_bone1:
#         raise Exception(f'Pose bone "{ik_joint1}" not found')
#     pos1 = pose_bone1.matrix.to_translation()

#     pose_bone2 = armature.pose.bones.get(ik_joint2)
#     if not pose_bone2:
#         raise Exception(f'Pose bone "{ik_joint2}" not found')
#     pos2 = pose_bone2.matrix.to_translation()

    pos = init_pos + src_obj.matrix_world.translation
    # keyframe = action.fcurves[0].keyframe_points.insert(frame, pos.x, options={'FAST'})
    # keyframe.interpolation = 'LINEAR'
    # keyframe = action.fcurves[1].keyframe_points.insert(frame, pos.z, options={'FAST'})
    # keyframe.interpolation = 'LINEAR'
    # keyframe = action.fcurves[2].keyframe_points.insert(frame, pos.y, options={'FAST'})
    # keyframe.interpolation = 'LINEAR'

    # quat = (src_obj.matrix_world.to_quaternion() @ init_rot)
    # keyframe = action.fcurves[3].keyframe_points.insert(frame, quat.w, options={'FAST'})
    # keyframe.interpolation = 'LINEAR'
    # keyframe = action.fcurves[4].keyframe_points.insert(frame, quat.x, options={'FAST'})
    # keyframe.interpolation = 'LINEAR'
    # keyframe = action.fcurves[5].keyframe_points.insert(frame, quat.y, options={'FAST'})
    # keyframe.interpolation = 'LINEAR'
    # keyframe = action.fcurves[6].keyframe_points.insert(frame, quat.z, options={'FAST'})
    # keyframe.interpolation = 'LINEAR'

    print(pos)

bpy.context.scene.frame_set(saved_frame)
