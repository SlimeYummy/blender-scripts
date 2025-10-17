import math
import bpy
from math_utils import near_int


cfg_scale = 0.6


def cfg_mapper(frame):
    # return frame <= 7 or near_int(frame)
    return False

active_action = bpy.context.view_layer.objects.active.animation_data.action

for fcurve in active_action.fcurves:
    prev_time = None

    # idx = 0
    # while idx < len(fcurve.keyframe_points):
    #     keyframe = fcurve.keyframe_points[idx]
    #     new_frame = keyframe.co[0] * cfg_scale
    #     if not cfg_filter(new_frame):
    #         fcurve.keyframe_points.remove(fcurve.keyframe_points[idx], fast=True)
    #     else:
    #         idx += 1
      
    for keyframe in fcurve.keyframe_points.items():
        keyframe.co[0] = keyframe.co[0] * cfg_scale
