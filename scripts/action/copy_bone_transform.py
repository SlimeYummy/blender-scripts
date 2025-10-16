import bpy
from mathutils import Quaternion, Vector


cfg_target = 'AxeArmature'


print('====================================')

if not bpy.context.selected_pose_bones or len(bpy.context.selected_pose_bones) != 2:
    raise Exception('Must select 2 bones')

from_bone = bpy.context.selected_pose_bones[0]
to_bone = bpy.context.selected_pose_bones[1]

print(f'From: {from_bone.name} To: {to_bone.name}')

loc = from_bone.matrix.translation - from_bone.bone.matrix_local.translation
to_bone.location = Vector((loc.x, loc.z, -loc.y))
print(f'Location: {to_bone.location}')

rot = from_bone.matrix.to_quaternion() @ from_bone.bone.matrix_local.to_quaternion().inverted()
to_bone.rotation_quaternion = Quaternion((rot.w, rot.x, rot.z, -rot.y))
print(f'Rotation: {to_bone.rotation_quaternion}')
