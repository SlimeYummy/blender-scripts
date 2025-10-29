import bpy
import math
import math_utils as mu
import re

from dataclasses import dataclass
from action_utils import travel_action_fcurves, search_fcurve, make_fcurve_id


cfg_dry_run = False

cfg_src_action = 'turn-l90-arp-raw'
cfg_src_start_frame = 1
cfg_src_finish_frame = 137

cfg_dst_action = 'turn-l90-arp-edit'
cfg_dst_start_frame = 1
cfg_dst_finish_frame = 137

cfg_location = True
cfg_euler = True
cfg_quaternion = False
cfg_scale = False

cfg_re_include = None
cfg_re_exclude = re.compile(r"^pose\.bones\[\"(:?J_Sec_|J_Adj_|c_pinky|c_ring|c_middle|c_index|c_thumb)")

active = bpy.context.view_layer.objects.active


@dataclass
class FcurveInfo:
    fcurve: bpy.types.FCurve
    start_value: float
    finish_value: float


def extract_fcurve_infos(name, start_frame, finish_frame) -> dict[str, FcurveInfo]:
    action = bpy.data.actions.get(name)
    if not action:
        raise Exception(f'Action "{name}" not found')
    active.animation_data.action = action

    infos = {}
    def visitor(fcurve):
        start = search_fcurve(fcurve, lambda keyframe: keyframe.co[0] == start_frame)
        if not start:
            raise Exception(f'No keyframe "{start_frame}" in "{fcurve.data_path}"')
        finish = search_fcurve(fcurve, lambda keyframe: keyframe.co[0] == finish_frame)
        if not finish:
            raise Exception(f'No keyframe "{finish_frame}" in "{fcurve.data_path}"')
        id  = make_fcurve_id(fcurve)
        infos[id] = FcurveInfo(fcurve, start.co[1], finish.co[1])

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
    return infos


if bpy.context.object.mode != 'POSE':
    raise Exception('Must in pose mode')

if cfg_src_finish_frame - cfg_src_start_frame != cfg_dst_finish_frame - cfg_dst_start_frame:
    raise Exception('Invalid start/finish frame')

src_fcurve_infos = extract_fcurve_infos(cfg_src_action, cfg_src_start_frame, cfg_src_finish_frame)
dst_fcurve_infos = extract_fcurve_infos(cfg_dst_action, cfg_dst_start_frame, cfg_dst_finish_frame)

for id, dst in dst_fcurve_infos.items():
    if cfg_dry_run:
        print(id, math.degrees(dst.start_value), math.degrees(dst.finish_value))
        continue

    src = src_fcurve_infos[id]
    start_diff = dst.start_value - src.start_value
    finish_diff = dst.finish_value - src.finish_value

    for keyframe in dst.fcurve.keyframe_points:
        if keyframe.co[0] == cfg_dst_start_frame or keyframe.co[0] == cfg_dst_finish_frame:
            keyframe.interpolation = 'LINEAR'

    src_frame = cfg_src_start_frame
    for dst_frame in range(cfg_dst_start_frame+1, cfg_dst_finish_frame):
        src_frame += 1

        t = (dst_frame - cfg_dst_start_frame) / (cfg_dst_finish_frame - cfg_dst_start_frame)
        value = src.fcurve.evaluate(src_frame) + mu.lerp(start_diff, finish_diff, t)
        # print(dst_frame, t, mu.lerp(start_diff, finish_diff, t), value)
        dst.fcurve.keyframe_points.insert(dst_frame, value, options={'FAST'})

if cfg_dry_run:
    print('\nIn dry run mode\n')
else:
    print('\nImitation completed\n')
