import bpy


print('====================================')

obj = bpy.context.view_layer.objects.active
if obj is None or obj.type != 'ARMATURE':
    raise Exception(f'Active object="{obj.name}" is not an armature')

bone = bpy.context.active_pose_bone
if bone is None:
    raise Exception('No active pose bone selected (need Pose mode)')

pos = (obj.matrix_world @ bone.matrix).translation


def draw_popup(self, context):
    layout = self.layout
    layout.label(text=f'Bone="{bone.name}" world location:')
    layout.label(text=f'x = {pos.x:.4f}, y = {pos.y:.4f}, z = {pos.z:.4f}')


bpy.context.window_manager.popup_menu(draw_popup, title='Bone Location')
