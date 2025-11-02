import bpy
from mathutils import Vector


cfg_target = 'AxeArmature'

cfg_center_offset = Vector((-0.025, -0.056, 0))


print('====================================')

weapons = []
for bone in bpy.context.selected_pose_bones:
    if bone.id_data.name != cfg_target:
        continue
    if 'Hand' not in bone.name:
        continue
    weapons.append(bone)
if len(weapons) == 0:
    raise Exception('No weapons selected')

for weapon in weapons:
    rest_pos = weapon.bone.matrix_local.translation
    old_hand_pos = Vector((weapon.location.x + rest_pos.x, weapon.location.y - rest_pos.z, 0))
    expected_len = cfg_center_offset.length
    new_hand_pos = old_hand_pos * (expected_len / old_hand_pos.length)
    new_pos = Vector((new_hand_pos.x - rest_pos.x, new_hand_pos.y + rest_pos.z, weapon.location.z))

    print('Rest:', weapon.bone.matrix_local.translation)
    print('Old local:', weapon.location)
    print('Old hand:', old_hand_pos)
    print('New hand:', new_hand_pos)
    print('New local:', new_hand_pos)

    weapon.location = new_pos
