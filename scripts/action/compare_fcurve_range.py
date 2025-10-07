import bpy
import math
from action_utils import make_fcurve_id, find_fcurve_by_id, get_selected_fcurves

cfg_action1 = 'Attack_1_2_#pre'
cfg_fcurve1 = 'c_root_master.x'
cfg_frame1 = [None, None]

cfg_action2 = 'Attack_1_1_#pre'
cfg_fcurve2 = 'c_root_master.x'
cfg_frame2 = [None, None]

cfg_types = [
    'location',
    'rotation_euler',
    # 'quaternion',
    # 'scale',
]


def calc_fcurve_range(fcurve, in_start = None, in_finish = None):
    start = in_start if in_start is not None else fcurve.keyframe_points[0].co[0]
    finish = in_finish if in_finish is not None else fcurve.keyframe_points[-1].co[0]
    min = math.inf
    max = -math.inf
    for frame in range(math.floor(start), math.ceil(finish) + 1):
        value = fcurve.evaluate(frame)
        min = min if min < value else value
        max = max if max > value else value
    return min, max


def collect_fcurve_ranges(action_name, types, in_start = None, in_finish = None):
    ranges = {}
    action = bpy.data.actions.get(action_name)
    if not action:
        raise Exception(f'Action "{action_name}" not found')
    for fcurve in action.fcurves:
        if f'["{cfg_fcurve1}"]' not in fcurve.data_path:
            continue
        for t in types:
            if f'.{t}' in fcurve.data_path:
                id= make_fcurve_id(fcurve)
                ranges[id] = calc_fcurve_range(fcurve, in_start, in_finish)
    return ranges


print('====================================')

print(cfg_action1, cfg_fcurve1)
print(cfg_action2, cfg_fcurve2)

ranges1 = collect_fcurve_ranges(cfg_action1, cfg_types, cfg_frame1[0], cfg_frame1[1])
ranges2 = collect_fcurve_ranges(cfg_action2, cfg_types, cfg_frame2[0], cfg_frame2[1])

for fcurve_id, range1 in ranges1.items():
    range2 = ranges2[fcurve_id]
    ratio = (range1[1] - range1[0]) / (range2[1] - range2[0])
    print(fcurve_id, ratio)
