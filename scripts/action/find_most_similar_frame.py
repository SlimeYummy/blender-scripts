import bpy
import math
import re
from dataclasses import dataclass
from action_utils import make_fcurve_id, travel_action_fcurves


cfg_find_action = 'Attack_1_1_raw'
cfg_cond_action = 'Attack_1_2_raw'
cfg_cond_frame = 0
cfg_location = False
cfg_euler = False
cfg_quaternion = True
cfg_scale = False

# cfg_re_include = re.compile(r"^pose\.bones\[\"(:?c_shoulder|c_arm_fk|c_forearm_fk|c_hand_fk)")
cfg_re_include = None
cfg_re_exclude = re.compile(r"^pose\.bones\[\"(:?J_Sec_|J_Adj_|c_pinky|c_ring|c_middle|c_index|c_thumb)")
cfg_re_exclude = None

active = bpy.context.view_layer.objects.active


def extract_all_values(name, start_frame = None, finish_frame = None):
    action = bpy.data.actions.get(name)
    if not action:
        raise Exception(f'Action "{name}" not found')
    active.animation_data.action = action

    fcurves = {}
    min_frame = math.inf
    max_frame = -math.inf
    
    def visitor(fcurve):
        nonlocal min_frame, max_frame
        min_frame = min(min_frame, fcurve.keyframe_points[0].co[0])
        max_frame = max(max_frame, fcurve.keyframe_points[-1].co[0])
        id = make_fcurve_id(fcurve)
        fcurves[id] = fcurve
    travel_action_fcurves(
        action,
        visitor,
        re_include=cfg_re_include,
        re_exclude=cfg_re_exclude,
        location=cfg_location,
        euler=cfg_euler,
        quaternion=cfg_quaternion,
        scale=cfg_scale
    )

    start_frame = min_frame if start_frame is None else start_frame
    finish_frame = max_frame if finish_frame is None else finish_frame
    if start_frame == math.inf or finish_frame == -math.inf:
        raise Exception(f'Invalid frame in action "{name}"')

    values = {}
    for frame in range(math.floor(start_frame), math.ceil(finish_frame + 1)):
        values[frame] = {}
        for id, fcurve in fcurves.items():
            values[frame][id] = fcurve.evaluate(frame)
    return values


@dataclass
class Diff:
    cond_frame: int
    find_frame: int
    diff_sq: float


if bpy.context.object.mode != 'POSE':
    raise Exception('Must in pose mode')

cond_values = extract_all_values(cfg_cond_action)
find_values = extract_all_values(cfg_find_action)

diffs = []
for cond_frame, cond_vals in cond_values.items():
    if cfg_cond_frame is not None and cond_frame != cfg_cond_frame:
        continue
    for find_frame, find_vals in find_values.items():
        diff_sq = 0
        for id, val in cond_vals.items():
            diff_sq += (val - find_vals[id]) ** 2
        diffs.append(Diff(cond_frame, find_frame, diff_sq))
        # print(f'{cond_frame} - {find_frame} | {diff_sq}')

sorted_diffs = sorted(diffs, key=lambda diff: diff.diff_sq)
frame = sorted_diffs[0].find_frame

# print(f'\nMatch bones list:')
# for id in cond_values[cfg_cond_frame or 1].keys():
#     print(f'{id}')

print(f'\nThe most similar frame:')
for idx in range(0, 50):
    if len(sorted_diffs) < idx:
        break
    print(f'{idx}: {sorted_diffs[idx].cond_frame} - {sorted_diffs[idx].find_frame} | {sorted_diffs[idx].diff_sq}')
