#
# 根据端点插值修改曲线
#

import bpy
import math_utils as mu
from action_utils import get_selected_fcurves


# ENDPOINT = 'left'
ENDPOINT = 'right'

# EASE_MODE = 'scale'
EASE_MODE = 'linear'
# EASE_MODE = 'quadIn'
# EASE_MODE = 'one'

FIRSET_OFFSET_RATIO = 0
# FIRSET_OFFSET_RATIO = 1


def apply_keyframe_value(kf, new_val):
    old_val = kf.co[1]
    delta = new_val - old_val
    kf.co[1] = new_val
    if kf.handle_left_type in ('FREE', 'ALIGNED'):
        kf.handle_left[1] += delta
    if kf.handle_right_type in ('FREE', 'ALIGNED'):
        kf.handle_right[1] += delta


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
    if start_idx is None or finish_idx is None:
        raise Exception('No selected keyframes')
    if EASE_MODE != 'one':
        if finish_idx - start_idx < 2:
            raise Exception('Selected keyframes < 3')
    else:
        if finish_idx - start_idx < 1:
            raise Exception('Selected keyframes < 2')

    fcurves_with_args.append((selected_fcurve, start_idx, finish_idx))

for selected_fcurve, start_idx, finish_idx in fcurves_with_args:
    keyframes = selected_fcurve.keyframe_points

    start_frame = keyframes[start_idx].co[0]
    if ENDPOINT == 'left' and FIRSET_OFFSET_RATIO == 0.0:
        start_frame = keyframes[start_idx + 1].co[0] # skip first keyframe if offset is 0

    finish_frame = keyframes[finish_idx].co[0]
    if ENDPOINT == 'right' and FIRSET_OFFSET_RATIO == 0.0:
        finish_frame = keyframes[finish_idx - 1].co[0] # skip last keyframe if offset is 0

    total_frame = finish_frame - start_frame
    total_old = keyframes[finish_idx].co[1] - keyframes[start_idx].co[1]

    if EASE_MODE == 'one' and total_frame == 0:
        if ENDPOINT == 'left':
            apply_keyframe_value(keyframes[finish_idx], keyframes[start_idx].co[1])
        else:
            apply_keyframe_value(keyframes[start_idx], keyframes[finish_idx].co[1])

    elif EASE_MODE != 'scale':
        if ENDPOINT == 'left':
            first_offset = (keyframes[start_idx + 2].co[1] - keyframes[start_idx + 1].co[1]) * FIRSET_OFFSET_RATIO
            total_diff = keyframes[start_idx].co[1] - keyframes[start_idx + 1].co[1] + first_offset

            for idx in range(start_idx + 1, finish_idx + 1, 1):
                t = (finish_frame - keyframes[idx].co[0]) / total_frame
                keyframes[idx].co[1] += mu.ease_func(EASE_MODE, t) * total_diff

        elif ENDPOINT == 'right':
            first_offset = (keyframes[finish_idx - 2].co[1] - keyframes[finish_idx - 1].co[1]) * FIRSET_OFFSET_RATIO
            total_diff = keyframes[finish_idx].co[1] - keyframes[finish_idx - 1].co[1] + first_offset

            for idx in range(finish_idx - 1, start_idx - 1, -1):
                t = (keyframes[idx].co[0] - start_frame) / total_frame
                keyframes[idx].co[1] += mu.ease_func(EASE_MODE, t) * total_diff

        else:
            raise Exception('Invalid ENDPOINT')

    else:
        if ENDPOINT == 'left':
            ref_val = keyframes[start_idx].co[1]
            first_old = keyframes[start_idx + 1].co[1]
            last_old = keyframes[finish_idx].co[1]
            first_offset = (keyframes[start_idx + 2].co[1] - keyframes[start_idx + 1].co[1]) * FIRSET_OFFSET_RATIO
            first_new = ref_val + first_offset

            ratio = (first_new - last_old) / (first_old - last_old)
            for idx in range(start_idx + 1, finish_idx + 1, 1):
                keyframes[idx].co[1] = last_old + (keyframes[idx].co[1] - last_old) * ratio

        elif ENDPOINT == 'right':
            ref_val = keyframes[finish_idx].co[1]
            first_old = keyframes[start_idx].co[1]
            last_old = keyframes[finish_idx - 1].co[1]
            last_offset = (keyframes[finish_idx - 2].co[1] - keyframes[finish_idx - 1].co[1]) * FIRSET_OFFSET_RATIO
            last_new = ref_val + last_offset

            ratio = (last_new - first_old) / (last_old - first_old)
            for idx in range(finish_idx - 1, start_idx - 1, -1):
                keyframes[idx].co[1] = first_old + (keyframes[idx].co[1] - first_old) * ratio

        else:
            raise Exception('Invalid ENDPOINT')
