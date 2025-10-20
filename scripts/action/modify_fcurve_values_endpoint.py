import bpy
import math_utils as mu
from action_utils import get_selected_fcurves


# endpoint = 'left'
endpoint = 'right'

ease_mode = 'scale'
# ease_mode = 'linear'
# ease_mode = 'quadIn'
# ease_mode = 'one'

# In = endpoint value
# Out = fcurve value

first_offset_ratio = 0.6


fcurves_with_args = []
selected_fcurves = get_selected_fcurves()
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
    if start_idx is None or finish_idx is None or finish_idx - start_idx < 2:
        print(start_idx, finish_idx)
        raise Exception('Selected keyframes < 3')

    fcurves_with_args.append((selected_fcurve, start_idx, finish_idx))

for selected_fcurve, start_idx, finish_idx in fcurves_with_args:
    keyframes = selected_fcurve.keyframe_points

    start_frame = keyframes[start_idx].co[0]
    if endpoint == 'left' and first_offset_ratio == 0.0:
        start_frame = keyframes[start_idx + 1].co[0] # skip first keyframe if offset is 0

    finish_frame = keyframes[finish_idx].co[0]
    if endpoint == 'right' and first_offset_ratio == 0.0:
        finish_frame = keyframes[finish_idx - 1].co[0] # skip last keyframe if offset is 0

    total_frame = finish_frame - start_frame
    total_old = keyframes[finish_idx].co[1] - keyframes[start_idx].co[1]

    if ease_mode != 'scale':
        if endpoint == 'left':
            first_offset = (keyframes[start_idx + 2].co[1] - keyframes[start_idx + 1].co[1]) * first_offset_ratio
            total_diff = keyframes[start_idx].co[1] - keyframes[start_idx + 1].co[1] + first_offset

            for idx in range(start_idx + 1, finish_idx + 1, 1):
                t = (finish_frame - keyframes[idx].co[0]) / total_frame
                keyframes[idx].co[1] += mu.ease_func(ease_mode, t) * total_diff

        elif endpoint == 'right':
            first_offset = (keyframes[finish_idx - 2].co[1] - keyframes[finish_idx - 1].co[1]) * first_offset_ratio
            total_diff = keyframes[finish_idx].co[1] - keyframes[finish_idx - 1].co[1] + first_offset

            for idx in range(finish_idx - 1, start_idx - 1, -1):
                t = (keyframes[idx].co[0] - start_frame) / total_frame
                keyframes[idx].co[1] += mu.ease_func(ease_mode, t) * total_diff

        else:
            raise Exception('Invalid endpoint')

    else:
        if endpoint == 'left':
            ref_val = keyframes[start_idx].co[1]
            first_old = keyframes[start_idx + 1].co[1]
            last_old = keyframes[finish_idx].co[1]
            first_offset = (keyframes[start_idx + 2].co[1] - keyframes[start_idx + 1].co[1]) * first_offset_ratio
            first_new = ref_val + first_offset

            ratio = (first_new - last_old) / (first_old - last_old)
            for idx in range(start_idx + 1, finish_idx + 1, 1):
                keyframes[idx].co[1] = last_old + (keyframes[idx].co[1] - last_old) * ratio

        elif endpoint == 'right':
            ref_val = keyframes[finish_idx].co[1]
            first_old = keyframes[start_idx].co[1]
            last_old = keyframes[finish_idx - 1].co[1]
            last_offset = (keyframes[finish_idx - 2].co[1] - keyframes[finish_idx - 1].co[1]) * first_offset_ratio
            print
            last_new = ref_val + last_offset

            ratio = (last_new - first_old) / (last_old - first_old)
            for idx in range(finish_idx - 1, start_idx - 1, -1):
                keyframes[idx].co[1] = first_old + (keyframes[idx].co[1] - first_old) * ratio

        else:
            raise Exception('Invalid endpoint')
