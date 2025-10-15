import bpy


def select_vrm_bones():
    if bpy.context.object.mode != 'POSE':
        raise Exception('Must in pose mode')
        
    active = bpy.context.view_layer.objects.active

    for b in active.pose.bones:
        b.bone.select = False

    names = [
        "J_Bip_C_Hips",
        "J_Bip_C_Spine",
        "J_Bip_C_Chest",
        "J_Bip_C_UpperChest",
        "J_Bip_C_Neck",
        "J_Bip_C_Head",
        "J_Bip_L_Shoulder",
        "J_Bip_L_UpperArm",
        "J_Bip_L_LowerArm",
        "J_Bip_L_Hand",
        "J_Bip_L_Index1",
        "J_Bip_L_Index2",
        "J_Bip_L_Index3",
        "J_Bip_L_Little1",
        "J_Bip_L_Little2",
        "J_Bip_L_Little3",
        "J_Bip_L_Middle1",
        "J_Bip_L_Middle2",
        "J_Bip_L_Middle3",
        "J_Bip_L_Ring1",
        "J_Bip_L_Ring2",
        "J_Bip_L_Ring3",
        "J_Bip_L_Thumb1",
        "J_Bip_L_Thumb2",
        "J_Bip_L_Thumb3",
        "J_Bip_R_Shoulder",
        "J_Bip_R_UpperArm",
        "J_Bip_R_LowerArm",
        "J_Bip_R_Hand",
        "J_Bip_R_Index1",
        "J_Bip_R_Index2",
        "J_Bip_R_Index3",
        "J_Bip_R_Little1",
        "J_Bip_R_Little2",
        "J_Bip_R_Little3",
        "J_Bip_R_Middle1",
        "J_Bip_R_Middle2",
        "J_Bip_R_Middle3",
        "J_Bip_R_Ring1",
        "J_Bip_R_Ring2",
        "J_Bip_R_Ring3",
        "J_Bip_R_Thumb1",
        "J_Bip_R_Thumb2",
        "J_Bip_R_Thumb3",
        "J_Bip_L_UpperLeg",
        "J_Bip_L_LowerLeg",
        "J_Bip_L_Foot",
        "J_Bip_L_ToeBase",
        "J_Bip_R_UpperLeg",
        "J_Bip_R_LowerLeg",
        "J_Bip_R_Foot",
        "J_Bip_R_ToeBase",
        # "J_Bip_L_LowerArm_Twist",
        # "J_Bip_R_LowerArm_Twist"
    ]

    for name in names:
        bone = active.pose.bones.get(name)
        if bone:
            bone.bone.select = True
            active.data.bones.active = bone.bone


select_vrm_bones()
