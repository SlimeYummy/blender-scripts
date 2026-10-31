import bpy


def select_arp_drivers(*, include_fingers = False, include_weapons = False):
    if bpy.context.object.mode != 'POSE':
        raise Exception('Must in pose mode')
        
    active = bpy.context.view_layer.objects.active

    for b in active.pose.bones:
        b.select = False

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

    if include_fingers:
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

    if include_weapons:
        names += [
            "Weapon_0_Root",
            "Weapon_1_Root",
            "WeaponControl_0",
            "WeaponControl_1",
        ]

    for name in names:
        bone = active.pose.bones.get(name)
        if bone:
            bone.select = True
            active.data.bones.active = bone.bone


def disable_arp_drivers(arp_rig, bone_name):
    bone = arp_rig.pose.bones.get(bone_name)
    if bone is None:
        raise RuntimeError(f'Pose bone "{bone_name}" not found on rig "{arp_rig.name}"')

    prefix = f'pose.bones["{bone_name}"].'
    for fcurve in arp_rig.animation_data.action.fcurves:
        if fcurve.data_path.startswith(prefix):
            fcurve.mute = True

    bone.location = (0.0, 0.0, 0.0)
    bone.rotation_euler = (0.0, 0.0, 0.0)
    bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
    bone.scale = (1.0, 1.0, 1.0)


def enable_arp_drivers(arp_rig, bone_name):
    prefix = f'pose.bones["{bone_name}"].'
    for fcurve in arp_rig.animation_data.action.fcurves:
        if fcurve.data_path.startswith(prefix):
            fcurve.mute = False
