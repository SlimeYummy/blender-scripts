import bpy


obj = bpy.context.view_layer.objects.active
if obj is None:
	raise Exception('No active object')
if obj.type != 'ARMATURE':
	raise Exception(f'Active object "{obj.name}" is not an Armature')
if obj.animation_data is None or obj.animation_data.action is None:
	raise Exception(f'Armature "{obj.name}" has no active action')


action = obj.animation_data.action
removed_count = 0

for fcurve in list(action.fcurves):
	if fcurve.data_path.endswith('.scale'):
		action.fcurves.remove(fcurve)
		removed_count += 1


print(f'Removed {removed_count} scale fcurves from action "{action.name}" on armature "{obj.name}"')
