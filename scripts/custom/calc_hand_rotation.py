import bpy
import math
from mathutils import Euler, Vector


cfg_target = 'AxeArmature'

cfg_left_diff = Euler((-math.pi, 0, math.pi / 2), 'XYZ').to_quaternion()
cfg_right_diff = Euler((-math.pi, 0, -math.pi / 2), 'XYZ').to_quaternion()

cfg_center_offset = Vector((-0.025, -0.056, 0))

cfg_left_plam = Vector((1, 0, 0, 0))
cfg_right_plam = Vector((-1, 0, 0, 0))


def calc_align_rot(hand, weapon):
    # print(hand.bone.matrix_local.to_euler())
    # print(hand.matrix.to_euler())
    # print(weapon.bone.matrix_local.to_euler())
    # print(weapon.matrix.to_euler())

    hand_diff = None
    if hand.name.endswith('.l'):
        hand_diff = cfg_left_diff
    elif hand.name.endswith('.r'):
        hand_diff = cfg_right_diff
    else:
        raise Exception(f'Unknown hand "{hand.name}"')

    weapon_rest = weapon.bone.matrix_local.to_quaternion()
    weapon_world = weapon.matrix.to_quaternion()
    
    align_rot = (hand_diff @ weapon_rest.inverted() @ weapon_world)
    return align_rot


def calc_center_rot(hand, weapon):
    rest_pos = weapon.bone.matrix_local.translation
    center_dir = cfg_center_offset

    weapon_dir = None
    center_rot = None
    if hand.name.endswith('.l'):
        weapon_dir = Vector((weapon.location.x + rest_pos.x, weapon.location.y - rest_pos.z, 0))
        center_rot = center_dir.rotation_difference(weapon_dir)
    elif hand.name.endswith('.r'):
        weapon_dir = Vector((-weapon.location.x + rest_pos.x, weapon.location.y - rest_pos.z, 0))
        center_rot = weapon_dir.rotation_difference(center_dir)
    else:
        raise Exception(f'Unknown hand "{hand.name}"')

    print('Rest:', weapon.bone.matrix_local.translation)
    print('Old local:', weapon.location)
    print('Weapon:', weapon_dir)
    return center_rot


print('====================================')

hands = []
for bone in bpy.context.selected_pose_bones:
    if 'c_hand_' not in bone.name:
        continue
    hands.append(bone)
if len(hands) == 0:
    raise Exception('No hands selected')

for hand in hands:
    armature = None
    weapon = None
    for constraint in hand.constraints:
        if constraint.type == 'COPY_LOCATION' and constraint.target.name == cfg_target:
            armature = constraint.target
            weapon = armature.pose.bones[constraint.subtarget]
            break
    if not weapon:
        raise Exception(f'No constraint for {hand.name}')

    align_rot = calc_align_rot(hand, weapon)
    hand.rotation_euler = align_rot.to_euler()
    center_rot = calc_center_rot(hand, weapon)
    hand.rotation_euler = (align_rot @ center_rot).to_euler()



# if not bpy.context.selected_objects or len() != 1:
#     raise Exception('Must select 1 hand')
# selected_hand = bpy.context.selected_objects[0]
# print(selected_hand.name)
