import bpy
import math
from mathutils import Quaternion, Euler
from action_utils import get_selected_fcurves, find_fcurve_by_id, action_frame_range


cfg_euler_type = 'XYZ'


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

if len(selected_fcurves) == 4:
    quat_fcurves = selected_fcurves
    for fcurve in quat_fcurves:
        if fcurve.data_path != 'rotation_quaternion' and not fcurve.data_path.endswith('.rotation_quaternion'):
            raise Exception('Only quaterion/euler rotation supported')
        
    sorted(quat_fcurves, key=lambda fcurve: fcurve.array_index)
    
    data_path = ''
    if quat_fcurves[0].data_path == 'rotation_quaternion':
        data_path = 'rotation_euler'
    else:
        data_path = fcurve.data_path[:-len('.rotation_quaternion')] + '.rotation_euler'

    euler_fcurves = []
    for idx, axis in enumerate(('x', 'y', 'z')):
        fcurve = find_fcurve_by_id(action, f"{data_path}.{axis}")
        if not fcurve:
            fcurve = action.fcurves.new(data_path=data_path, index=idx, action_group=quat_fcurves[0].group.name)
        euler_fcurves.append(fcurve)

    for frame in action_frame_range(action):
        quat = Quaternion()
        for i, curve in enumerate(quat_fcurves):
            quat[curve.array_index] = curve.evaluate(frame)
        euler = quat.to_euler(cfg_euler_type)
        for axis in range(3):
            euler_fcurves[axis].keyframe_points.insert(frame, euler[axis])
    
elif len(selected_fcurves) == 3:
    euler_fcurves = selected_fcurves
    for fcurve in euler_fcurves:
        print(">>>>>>>>>>", fcurve.data_path, fcurve.data_path.endswith('.rotation_euler'))
        if fcurve.data_path != 'rotation_euler' and not fcurve.data_path.endswith('.rotation_euler'):
            raise Exception('Only quaterion/euler rotation supported')

    sorted(euler_fcurves, key=lambda fcurve: fcurve.array_index)

    data_path = ''
    if euler_fcurves[0].data_path == 'rotation_euler':
        data_path = 'rotation_quaternion'
    else:
        data_path = fcurve.data_path[:-len('.rotation_euler')] + '.rotation_quaternion'

    quat_fcurves = []
    for idx, axis in enumerate(('x', 'y', 'z', 'w')):
        fcurve = find_fcurve_by_id(action, f"{data_path}.{axis}")
        if not fcurve:
            fcurve = action.fcurves.new(data_path=data_path, index=idx, action_group=euler_fcurves[0].group.name)
        quat_fcurves.append(fcurve)

    for frame in action_frame_range(action):
        euler = []
        for i, curve in enumerate(euler_fcurves):
            euler.append(curve.evaluate(frame))
        quat = Euler(euler, cfg_euler_type).to_quaternion()
        for axis in range(4):
            quat_fcurves[axis].keyframe_points.insert(frame, quat[axis])

else:
    raise Exception('Only quaterion/euler rotation supported')
