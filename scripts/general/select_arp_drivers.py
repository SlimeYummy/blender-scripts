import bpy


cfg_include_hand = True
# cfg_include_hand = False


def select_vrm_bones():
    if bpy.context.object.mode != 'POSE':
        raise Exception('Must in pose mode')
        
    active = bpy.context.view_layer.objects.active

    for b in active.pose.bones:
        b.bone.select = False

    names = [
        "c_root_master.x",
        "c_spine_01.x",
        "c_spine_02.x",
        "c_spine_03.x",
        "c_shoulder.l",
        "c_arm_fk.l",
        "c_forearm_fk.l",
        "c_hand_fk.l",
        "c_arm_ik.l",
        "c_hand_ik.l",
        "c_arms_pole.l",
        "c_shoulder.r",
        "c_arm_fk.r",
        "c_forearm_fk.r",
        "c_hand_fk.r",
        "c_arm_ik.r",
        "c_hand_ik.r",
        "c_arms_pole.r",
        "c_neck.x",
        "c_head.x",
        "c_thigh_fk.l",
        "c_leg_fk.l",
        "c_foot_fk.l",
        "c_thigh_ik.l",
        "c_foot_ik.l",
        "c_toes_ik.l",
        "c_leg_pole.l",
        "c_thigh_fk.r",
        "c_leg_fk.r",
        "c_foot_fk.r",
        "c_thigh_ik.r",
        "c_foot_ik.r",
        "c_toes_ik.r",
        "c_leg_pole.r",
    ]

    if cfg_include_hand:
        names += [
            "c_pinky1.l",
            "c_pinky2.l",
            "c_pinky3.l",
            "c_ring1.l",
            "c_ring2.l",
            "c_ring3.l",
            "c_middle1.l",
            "c_middle2.l",
            "c_middle3.l",
            "c_index1.l",
            "c_index2.l",
            "c_index3.l",
            "c_thumb1.l",
            "c_thumb2.l",
            "c_thumb3.l",
            "c_pinky1.r",
            "c_pinky2.r",
            "c_pinky3.r",
            "c_ring1.r",
            "c_ring2.r",
            "c_ring3.r",
            "c_middle1.r",
            "c_middle2.r",
            "c_middle3.r",
            "c_index1.r",
            "c_index2.r",
            "c_index3.r",
            "c_thumb1.r",
            "c_thumb2.r",
            "c_thumb3.r",
        ]

    for name in names:
        bone = active.pose.bones.get(name)
        if bone:
            bone.bone.select = True
            active.data.bones.active = bone.bone


select_vrm_bones()
