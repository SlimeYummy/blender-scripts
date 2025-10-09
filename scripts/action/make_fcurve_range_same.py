import bpy
import math
from action_utils import make_fcurve_id, find_fcurve_by_id, get_selected_fcurves


# cfg_dry_run = False
cfg_dry_run = True

# cfg_reference_action = None
cfg_reference_action = 'jog_arp_bake'

cfg_reference_start_frame = 1
cfg_reference_finish_frame = 57
cfg_selected_start_frame = 1
cfg_selected_finish_frame = 57

# cfg_reference_start_frame = None
# cfg_reference_finish_frame = None
# cfg_selected_start_frame = None
# cfg_selected_finish_frame = None


def calc_fcurve_range(fcurve, in_start, in_finish):
    start = in_start if in_start is not None else fcurve.keyframe_points[0].co[0]
    finish = in_finish if in_finish is not None else fcurve.keyframe_points[-1].co[0]
    min = math.inf
    max = -math.inf
    for frame in range(math.floor(start), math.ceil(finish) + 1):
        value = fcurve.evaluate(frame)
        min = min if min < value else value
        max = max if max > value else value
    return min, max


def calc_reference_fcurve_range(action_name, fcurve_id, in_start, in_finish):
    action = bpy.data.actions.get(action_name)
    if not action:
        raise Exception(f'Action "{action_name}" not found')
    fcurve = find_fcurve_by_id(action, fcurve_id)
    return calc_fcurve_range(fcurve, in_start, in_finish)


selected_fcurves = get_selected_fcurves()
for selected_fcurve in selected_fcurves:
    selected_range = calc_fcurve_range(
        selected_fcurve,
        cfg_selected_start_frame,
        cfg_selected_finish_frame
    )
    selected_id = make_fcurve_id(selected_fcurve)
    refer_range = calc_reference_fcurve_range(
        cfg_reference_action,
        selected_id,
        cfg_reference_start_frame,
        cfg_reference_finish_frame
    )

    print(f"\n{selected_id}")
    print(f"reference range: {math.degrees(refer_range[0])} {math.degrees(refer_range[1])}")
    print(f"selected range: {math.degrees(selected_range[0])} {math.degrees(selected_range[1])}")

    scale = (refer_range[1] - refer_range[0]) / (selected_range[1] - selected_range[0])
    translate = (refer_range[1] + refer_range[0]) / 2 - (selected_range[1] + selected_range[0]) / 2

    is_euler = selected_id.find('.rotation_euler.') != -1
    print(f'scale: {scale}')
    print(f'translate: {translate if not is_euler else math.degrees(translate)}')

    if not cfg_dry_run:
        new_mid = (selected_range[1] + selected_range[0]) / 2 + translate
        for keyframe in selected_fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'
            keyframe.co[1] = new_mid + (keyframe.co[1] + translate - new_mid) * scale
