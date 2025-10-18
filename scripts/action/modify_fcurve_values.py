import bpy
import math
from action_utils import get_selected_fcurves


move_raw = 0.0
move_fin = 0.0

scale = 0.7
# scale_center = 0.5 # by center
# scale_center = 0.0 # by min
# scale_center = 1.0 # by max
# scale_center = 'first' # by first
scale_center = 'last' # by last

fcurves_with_args = []
selected_fcurves = get_selected_fcurves()
print(selected_fcurves)
for selected_fcurve in selected_fcurves:
    keyframes = selected_fcurve.keyframe_points

    start_idx = None
    finish_idx = None
    for idx, keyframe in enumerate(keyframes):
        if keyframe.select_control_point:
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
    if type(scale_center) == float:
        sc = scale_center
    elif scale_center == 'first':
        sc = (keyframes[start_idx].co[1] - min_val) / (max_val - min_val)
    elif scale_center == 'last':
        sc = (keyframes[finish_idx].co[1] - min_val) / (max_val - min_val)
    else:
        raise Exception('Invalid scale_center')

    scale_ref = min_val * (1.0 - sc) + max_val * sc + move_raw
    for idx in range(start_idx, finish_idx + 1):
        value = keyframes[idx].co[1]
        keyframes[idx].co[1] = (value - scale_ref) * scale + scale_ref + move_fin
