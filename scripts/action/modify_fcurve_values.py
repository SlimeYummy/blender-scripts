#
# 根据相对值平移/缩放修改曲线
#

import bpy
import math
from action_utils import get_selected_fcurves, find_fingers_fcurves


MOVE_RAW = 0.0
MOVE_FIN = 0.0

# SCALE = 0.9
# SCALE = 1.5
# SCALE_CENTER = 0.5 # by center
# SCALE_CENTER = 0.0 # by min
# SCALE_CENTER = 1.0 # by max
SCALE_CENTER = 'first' # by first
# SCALE_CENTER = 'last' # by last

AUTO_SELECT_ALL = True

selected_fcurves = get_selected_fcurves()
print(selected_fcurves)

# selected_fcurves = find_fingers_fcurves(
#     bpy.context.view_layer.objects.active.animation_data.action,
#     list_transform=['rotation_euler']
# )
# print(len(selected_fcurves))

fcurves_with_args = []
for selected_fcurve in selected_fcurves:
    keyframes = selected_fcurve.keyframe_points

    start_idx = None
    finish_idx = None
    for idx, keyframe in enumerate(keyframes):
        if keyframe.select_control_point or AUTO_SELECT_ALL:
            if start_idx == None:
                start_idx = idx
                finish_idx = idx
            elif finish_idx + 1 == idx:
                finish_idx = idx
            else:
                raise Exception('Selected keyframes not continuous')
    if start_idx is None or finish_idx is None or finish_idx == start_idx:
        raise Exception('Selected keyframes < 1')

    fcurves_with_args.append((selected_fcurve, start_idx, finish_idx))

for selected_fcurve, start_idx, finish_idx in fcurves_with_args:
    keyframes = selected_fcurve.keyframe_points

    min_val = math.inf
    max_val = -math.inf
    for idx in range(start_idx, finish_idx + 1):
        value = keyframes[idx].co[1]
        min_val = min(min_val, value)
        max_val = max(max_val, value)

    sc: float
    if type(SCALE_CENTER) == float:
        sc = SCALE_CENTER
    elif SCALE_CENTER == 'first':
        sc = (keyframes[start_idx].co[1] - min_val) / (max_val - min_val)
    elif SCALE_CENTER == 'last':
        sc = (keyframes[finish_idx].co[1] - min_val) / (max_val - min_val)
    else:
        raise Exception('Invalid SCALE_CENTER')

    scale_ref = min_val * (1.0 - sc) + max_val * sc + MOVE_RAW
    for idx in range(start_idx, finish_idx + 1):
        value = keyframes[idx].co[1]
        keyframes[idx].co[1] = (value - scale_ref) * SCALE + scale_ref + MOVE_FIN
