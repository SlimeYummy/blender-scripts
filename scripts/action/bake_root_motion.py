#
# 将动画中某骨骼的运动作为 Root Motion，烘焙到目标骨骼上。
#

import bpy
from action_utils import find_fcurve_by_id


class RootMotionMeta:
    action: str
    sequences: list[tuple[int, int, str]]

    def __init__(self, action, sequences):
        self.action = action
        self.sequences = sequences


CFG_METAS = [
    RootMotionMeta('Attack_01A_#edit2', [
        (0, 84, 'c_foot_ik.l'),
    ]),
    RootMotionMeta('Attack_02A_#edit2', [
        (0, 84, 'c_foot_ik.l'),
    ]),
    # RootMotionMeta('Attack_01B_#edit2', [
    #     (0, 17, 'c_foot_ik.r'),
    #     (10, 53, 'c_foot_ik.l'),
    # ]),
    # RootMotionMeta('Attack_02B_#edit2', [
    #     (0, 17, 'c_foot_ik.r'),
    #     (18, 58, 'c_foot_ik.l'),
    # ]),
    RootMotionMeta('Attack_03A_#edit2', [
        (0, 13, 'c_foot_ik.l'),
        (14, 68, 'c_foot_ik.r'),
        (69, 85, 'c_foot_ik.l'),
    ]),
    RootMotionMeta('Attack_04A_#edit2', [
        (0, 57, 'c_foot_ik.r'),
        (58, 85, 'c_foot_ik.l'),
    ]),


    RootMotionMeta('Walk_Empty_#edit', [
        (0, 25, 'c_foot_ik.l'),
        (26, 34, 'c_toes_ik.l'),
        (35, 59, 'c_foot_ik.r'),
        (60, 68, 'c_toes_ik.r'),
    ]),
    RootMotionMeta('Walk_Start_Axe_#edit', [
        (0, 11, 'c_foot_ik.r'),
        (12, 20, 'c_toes_ik.r'),
    ]),
    
    RootMotionMeta('Dodge_Empty_F_#edit', [
        (27, 42, 'c_foot_ik.r'),
    ]),
    RootMotionMeta('Dodge_Axe_F_#edit', [
        (27, 42, 'c_foot_ik.r'),
    ]),

    
    RootMotionMeta('UE_Hit_B_remap', [
        (1, 52, 'J_Bip_L_Foot'),
    ]),
    RootMotionMeta('UE_Hit_F_remap', [
        (1, 30, 'J_Bip_L_Foot'),
        (31, 52, 'J_Bip_R_Foot'),
    ]),
    RootMotionMeta('UE_Hit_L_remap', [
        (1, 52, 'J_Bip_R_Foot'),
    ]),
    RootMotionMeta('UE_Hit_R_remap', [
        (1, 52, 'J_Bip_L_Foot'),
    ]),
    RootMotionMeta('UE_Hit_Large_B_remap', [
        (1, 23, 'J_Bip_R_ToeBase'),
        (24, 62, 'J_Bip_L_ToeBase'),
    ]),
    RootMotionMeta('UE_Hit_Large_F_remap', [
        (1, 14, 'J_Bip_L_ToeBase'),
        (19, 62, 'J_Bip_R_ToeBase'),
    ]),
    RootMotionMeta('UE_Hit_Large_L_remap', [
        (1, 8, 'J_Bip_L_ToeBase'),
        (14, 62, 'J_Bip_R_ToeBase'),
    ]),
    RootMotionMeta('UE_Hit_Large_R_remap', [
        (1, 12, 'J_Bip_R_ToeBase'),
        (15, 62, 'J_Bip_L_ToeBase'),
    ]),
]


# local: 根据骨骼local位移计算，一般适用IK骨骼。
# world: 根据骨骼world位移计算，一般适用FK骨骼。
SRC_MODE = 'world'
SRC_AXIS = 'y'

# DST_BONE = 'J_Bip_C_Hips'
DST_BONE = 'c_pos'
DST_FCURVE = f'pose.bones["{DST_BONE}"].location'
DST_AXIS = 'y'

# START_MOTION = -0.03
START_MOTION = 0


AXIS_INDEX = {'x': 0, 'y': 1, 'z': 2}

def get_axis_index(axis):
    index = AXIS_INDEX.get(axis)
    if index is None:
        raise Exception(f'Unexpected axis "{axis}"')
    return index


def evaluate_src_value(obj, bone):
    if SRC_MODE == 'local':
        return bone.location[get_axis_index(SRC_AXIS)]

    elif SRC_MODE == 'world':
        world_pos = (obj.matrix_world @ bone.matrix).translation
        return world_pos[get_axis_index(SRC_AXIS)]

    else:
        raise Exception(f'Unexpected source mode "{SRC_MODE}"')


def calculate_world_dst_value(obj, bone, value):
    world_matrix = (obj.matrix_world @ bone.matrix).copy()
    world_pos = world_matrix.to_translation()
    world_pos[get_axis_index(DST_AXIS)] += value
    world_matrix.translation = world_pos

    local_matrix = obj.convert_space(
        pose_bone=bone,
        matrix=world_matrix,
        from_space='WORLD',
        to_space='LOCAL',
    )
    return local_matrix.to_translation()


def write_local_dst_value(active_action, dst_values):
    dst_fcurve = find_fcurve_by_id(active_action, f'{DST_FCURVE}.{DST_AXIS}')
    if dst_fcurve:
        dst_fcurve.keyframe_points.clear()
    else:
        index = get_axis_index(DST_AXIS)
        dst_fcurve = active_action.fcurves.new(DST_FCURVE, index=index, action_group='c_pos')

    for frame, dst_value in dst_values:
        keyframe = dst_fcurve.keyframe_points.insert(frame, dst_value, options={'FAST'})
        keyframe.interpolation = 'LINEAR'


def write_world_dst_value(active_action, dst_values):
    dst_fcurve_x = find_fcurve_by_id(active_action, f'{DST_FCURVE}.x')
    dst_fcurve_y = find_fcurve_by_id(active_action, f'{DST_FCURVE}.y')
    dst_fcurve_z = find_fcurve_by_id(active_action, f'{DST_FCURVE}.z')
    
    for frame, dst_value in dst_values:
        if DST_AXIS == 'x':
            keyframe_x = dst_fcurve_x.keyframe_points.insert(frame, dst_value.x, options={'FAST'})
            keyframe_x.interpolation = 'LINEAR'
        elif DST_AXIS == 'y':
            keyframe_y = dst_fcurve_y.keyframe_points.insert(frame, dst_value.y, options={'FAST'})
            keyframe_y.interpolation = 'LINEAR'
        elif DST_AXIS == 'z':
            keyframe_z = dst_fcurve_z.keyframe_points.insert(frame, dst_value.z, options={'FAST'})
            keyframe_z.interpolation = 'LINEAR'


def main():
    active_obj = bpy.context.view_layer.objects.active
    active_action = active_obj.animation_data.action

    meta = next(filter(lambda x: x.action == active_action.name, CFG_METAS), None)
    if not meta:
        raise Exception(f'Meta not found "{active_action.name}"')

    print('src action:', meta.action)
    print('sequences:', meta.sequences)
    
    dst_bone = active_obj.pose.bones.get(DST_BONE)
    if not dst_bone:
        raise Exception(f'Pose bone not found "{DST_BONE}"')

    saved_frame = bpy.context.scene.frame_current
    total_motion = START_MOTION
    dst_values = []
    try:
        for idx, (start, finish, bone_name) in enumerate(meta.sequences):
            src_bone = active_obj.pose.bones.get(bone_name)
            if not src_bone:
                raise Exception(f'Pose bone not found "{bone_name}"')

            prev_frame = start if idx == 0 else start - 1
            bpy.context.scene.frame_set(prev_frame)
            prev_val = evaluate_src_value(active_obj, src_bone)

            for frame in range(start, finish + 1):
                bpy.context.scene.frame_set(frame)
                cur_val = evaluate_src_value(active_obj, src_bone)
                total_motion = total_motion - (cur_val - prev_val)
                prev_val = cur_val

                if SRC_MODE == 'local':
                    dst_values.append((frame, total_motion))
                    print(frame, total_motion)
                elif SRC_MODE == 'world':
                    world_motion = calculate_world_dst_value(active_obj, dst_bone, total_motion)
                    dst_values.append((frame, world_motion))
                    print(frame, world_motion)
        
        if SRC_MODE == 'local':
            write_local_dst_value(active_action, dst_values)
        elif SRC_MODE == 'world':
            write_world_dst_value(active_action, dst_values)

    finally:
        bpy.context.scene.frame_set(saved_frame)


print('====================================')
main()
