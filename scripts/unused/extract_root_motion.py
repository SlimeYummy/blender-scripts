import bpy
from mathutils import Quaternion, Euler
from action_utils import action_frame_range


extract_position = None
extract_rotation = 'y'

euler_mode = 'YXZ'

# src_bone = 'c_root_master.x'
# dst_bone = 'c_traj'

src_bone = 'J_Bip_C_Hips'
dst_bone = 'Root'


def get_rotation_mode(name):
    for bone in bpy.context.object.pose.bones:
        if bone.name == name:
            return bone.rotation_mode


def collect_quaternions(action, rot_mode):
    if rot_mode == 'QUATERNION':
        fcurves = [None, None, None, None]
        for fcurve in active_action.fcurves:
            if fcurve.data_path == f'pose.bones["{src_bone}"].rotation_quaternion':
                fcurves[fcurve.array_index] = fcurve
        
        quats = []
        for frame in action_frame_range(action):
            quat = Quaternion()
            for fcurve in fcurves:
                quat[fcurve.array_index] = fcurve.evaluate(frame)
            quats.append(quat)
        return quats

    else:
        fcurves = [None, None, None]
        for fcurve in active_action.fcurves:
            if fcurve.data_path == f'pose.bones["{src_bone}"].rotation_euler':
                fcurves[fcurve.array_index] = fcurve
        
        quats = []
        for frame in action_frame_range(action):
            angles = [None, None, None]
            for fcurve in fcurves:
                angles[fcurve.array_index] = fcurve.evaluate(frame)
            euler = Euler(angles, rot_mode)
            quats.append(euler.to_quaternion())
        return quats


def extract_dst_quaternions(action, src_quats, components):
    dst_quats = []
    for idx, frame in enumerate(action_frame_range(action)):
        src_rot = src_quats[idx].to_euler('YXZ')
        angles = [0, 0, 0]
        if 'x' in components:
            angles[0] = src_rot.x
        if 'y' in components:
            angles[1] = src_rot.y
        if 'z' in components:
            angles[2] = src_rot.z
        print(src_rot.x, src_rot.y, src_rot.z)
        dst_quats.append(Euler(angles, 'YXZ').to_quaternion())
    return dst_quats


def recalculate_src_quaternions(src_quats, dst_quats):
    new_src_quats = []
    for idx in range(len(src_quats)):
        src_quat = src_quats[idx]
        dst_quat = dst_quats[idx]
        new_src_quats.append(dst_quat.conjugated() * src_quat)
    return new_src_quats


def write_rotations(action, rot_mode, bone_name, quats):
    if rot_mode == 'QUATERNION':
        fcurves = [None, None, None, None]
        for fcurve in active_action.fcurves:
            if fcurve.data_path == f'pose.bones["{bone_name}"].rotation_quaternion':
                fcurves[fcurve.array_index] = fcurve
        
        for idx, fcurve in enumerate(fcurves):
            if fcurve is None:
                fcurves[idx] = action.fcurves.new(data_path=f'pose.bones["{bone_name}"].rotation_quaternion', index=idx, action_group=bone_name)
            else:
                fcurve.keyframe_points.clear()

        for idx, frame in enumerate(action_frame_range(action)):
            quat = quats[idx]
            fcurves[0].keyframe_points.insert(frame, quat.w, options={'FAST'})
            fcurves[1].keyframe_points.insert(frame, quat.x, options={'FAST'})
            fcurves[2].keyframe_points.insert(frame, quat.y, options={'FAST'})
            fcurves[3].keyframe_points.insert(frame, quat.z, options={'FAST'})

    else:
        fcurves = [None, None, None]
        for fcurve in active_action.fcurves:
            if fcurve.data_path == f'pose.bones["{bone_name}"].rotation_euler':
                fcurves[fcurve.array_index] = fcurve
        
        for idx, fcurve in enumerate(fcurves):
            if fcurve is None:
                fcurves[idx] = action.fcurves.new(data_path=f'pose.bones["{bone_name}"].rotation_euler', index=idx, action_group=bone_name)
            else:
                fcurve.keyframe_points.clear()

        for idx, frame in enumerate(action_frame_range(action)):
            quat = quats[idx]
            angles = quat.to_euler(rot_mode)
            fcurves[0].keyframe_points.insert(frame, angles.x, options={'FAST'})
            fcurves[1].keyframe_points.insert(frame, angles.y, options={'FAST'})
            fcurves[2].keyframe_points.insert(frame, angles.z, options={'FAST'})


print()

active = bpy.context.view_layer.objects.active
active_action = bpy.context.view_layer.objects.active.animation_data.action

src_rot_mode = get_rotation_mode(src_bone)
dst_rot_mode = get_rotation_mode(dst_bone)
print(f"src rotation: {src_rot_mode}")
print(f"dst rotation: {dst_rot_mode}")

src_quats = collect_quaternions(active_action, src_rot_mode)
dst_quats = extract_dst_quaternions(active_action, src_quats, extract_rotation)
new_src_quats = recalculate_src_quaternions(src_quats, dst_quats)

print(new_src_quats)

# write_rotations(active_action, dst_rot_mode, dst_bone, dst_quats)
# write_rotations(active_action, src_rot_mode, src_bone, new_src_quats)
