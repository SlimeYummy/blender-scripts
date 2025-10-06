import bpy
from mathutils import Euler
from action_utils import get_selected_fcurves, action_frame_range


cfg_euler_type_in = 'XYZ'
cfg_euler_type_out = 'YXZ'
# cfg_euler_type_out = 'ZXY'

cfg_mode = 'point'
# cfg_mode = 'frame'


selected_fcurves = get_selected_fcurves()

action = None
for fcurve in selected_fcurves:
    if isinstance(fcurve.id_data, bpy.types.Action):
        if action == None:
            action = fcurve.id_data
        elif action != fcurve.id_data:
            raise Exception('All fcurves must in same action')
    else:
        raise Exception('Fcurve action not found')

if len(selected_fcurves) != 3:
    raise Exception('Only euler rotation supported')

fcurves = selected_fcurves
for fcurve in fcurves:
    if fcurve.data_path != 'rotation_euler' and not fcurve.data_path.endswith('.rotation_euler'):
        raise Exception('Only euler rotation supported')

sorted(fcurves, key=lambda fcurve: fcurve.array_index)

data_path = ''
if fcurves[0].data_path == 'rotation_euler':
    data_path = 'rotation_quaternion'
else:
    data_path = fcurve.data_path[:-len('.rotation_euler')] + '.rotation_quaternion'

if cfg_mode == 'frame':
    euler_outs = []
    for frame in action_frame_range(action):
        euler_in = [
            fcurves[0].evaluate(frame),
            fcurves[1].evaluate(frame),
            fcurves[2].evaluate(frame)
        ]
        quat = Euler(euler_in, cfg_euler_type_in).to_quaternion()
        euler_outs.append(quat.to_euler(cfg_euler_type_out))
        print(euler_in, euler_outs[-1])

    fcurves[0].keyframe_points.clear()
    fcurves[1].keyframe_points.clear()
    fcurves[2].keyframe_points.clear()
    for idx, frame in enumerate(action_frame_range(action)):
        keyframe = fcurves[0].keyframe_points.insert(frame, euler_outs[idx].x, options={'FAST'})
        keyframe.interpolation = 'LINEAR'
        keyframe =  fcurves[1].keyframe_points.insert(frame, euler_outs[idx].y, options={'FAST'})
        keyframe.interpolation = 'LINEAR'
        keyframe = fcurves[2].keyframe_points.insert(frame, euler_outs[idx].z, options={'FAST'})
        keyframe.interpolation = 'LINEAR'

elif cfg_mode == 'point':
    for idx in range(0, len(fcurves[0].keyframe_points)):
        euler_in = [
            fcurves[0].keyframe_points[idx].co[1],
            fcurves[1].keyframe_points[idx].co[1],
            fcurves[2].keyframe_points[idx].co[1]
        ]
        quat = Euler(euler_in, cfg_euler_type_in).to_quaternion()
        euler_out = quat.to_euler(cfg_euler_type_out)
        fcurves[0].keyframe_points[idx].co[1] = euler_out.x
        fcurves[1].keyframe_points[idx].co[1] = euler_out.y
        fcurves[2].keyframe_points[idx].co[1] = euler_out.z
