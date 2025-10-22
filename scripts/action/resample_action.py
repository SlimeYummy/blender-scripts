import math
import bpy
from math_utils import ease_func


def timestamps():
    # for t in range(1, 26, 2):
    #     yield t

    # t = 25
    # for p in range(6, 0, -1):
    #     t += 1.5 + 0.5 * p / 7
    #     yield t
    t = 0
    while t < 79:
        t = min(79, t + 1.5)
        yield t

print(list(timestamps()))


active_action = bpy.context.view_layer.objects.active.animation_data.action

for fcurve in active_action.fcurves:
    points = []
    for tm in timestamps():
        value = fcurve.evaluate(tm)
        points.append(value)

    fcurve.keyframe_points.clear()
    for tm, value in enumerate(points):
        keyframe = fcurve.keyframe_points.insert(tm, value, options={'FAST'})
        keyframe.interpolation = 'LINEAR'
