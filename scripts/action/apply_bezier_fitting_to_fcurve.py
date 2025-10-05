import bpy
import math
import mathutils as mu
import numpy as np
import scipy.optimize as sci_optimize


def apply_bezier_fitting():
    fcurves = None
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'GRAPH_EDITOR':
                with bpy.context.temp_override(window=window, area=area):
                    fcurves = bpy.context.selected_visible_fcurves
                break
    if fcurves is None or len(fcurves) == 0:
        raise Exception('No fcurves selected')
    
    fcurve = None
    for fc in fcurves:
        if fc.lock or fc.hide:
            continue
        if fcurve:
            raise Exception('Multiple fcurves selected')
        fcurve = fc
    keyframe_points = fcurve.keyframe_points

    first_idx = -1
    last_idx = -1
    for idx, keyframe in enumerate(keyframe_points):
        if keyframe.select_control_point:
            if first_idx == -1:
                first_idx = idx
                last_idx = idx
            elif keyframe_points[last_idx].select_control_point:
                last_idx = idx
            else:
                raise Exception('Non-continuous keyframes')
    if last_idx - first_idx <= 0:
        raise Exception('Not enough keyframes')

    samplings = sample_points(fcurve, first_idx, last_idx)
    (ctrl1, ctrl2) = fit_bezier(samplings, np.array([
        keyframe_points[first_idx].co,
        keyframe_points[last_idx].co,
    ]))

    keyframe_points[first_idx].interpolation = 'BEZIER'
    keyframe_points[first_idx].handle_right_type = 'FREE'
    keyframe_points[first_idx].handle_right = mu.Vector((ctrl1[0], ctrl1[1]))
    # keyframe_points[last_idx].interpolation = 'BEZIER'
    keyframe_points[last_idx].handle_left_type = 'FREE'
    keyframe_points[last_idx].handle_left = mu.Vector((ctrl2[0], ctrl2[1]))

    first_frame = keyframe_points[first_idx].co[0]
    last_frame = keyframe_points[last_idx].co[0]
    idx = 0
    while idx < len(keyframe_points):
        frame = keyframe_points[idx].co[0]
        if frame > first_frame and frame < last_frame:
            keyframe_points.remove(keyframe_points[idx], fast=True)
        else:
            idx += 1


def sample_points(fcurve, first_idx, last_idx):
    pts = np.array([(kf.co[0], kf.co[1]) for kf in fcurve.keyframe_points[first_idx:last_idx + 1]])
    samplings = np.empty((len(pts) + len(pts) - 1 + 2, 2))
    samplings[0] = pts[0]
    ptr = 1
    for idx in range(1, len(pts)):
        prev = pts[idx-1]
        curr = pts[idx]
        if idx == 1 or idx == len(pts) - 1:
            samplings[ptr][0] = prev[0] + (curr[0] - prev[0]) / 3
            samplings[ptr][1] = fcurve.evaluate(samplings[ptr][0])
            samplings[ptr+1][0] = prev[0] + (curr[0] - prev[0]) / 3 * 2
            samplings[ptr+1][1] = fcurve.evaluate(samplings[ptr+1][0])
            samplings[ptr+2] = curr
            ptr += 3
        else:
            samplings[ptr][0] = (prev[0] + curr[0]) / 2
            samplings[ptr][1] = fcurve.evaluate(samplings[ptr][0])
            samplings[ptr+1] = curr
            ptr += 2
    return samplings


def fit_bezier(samplings, init_ctrls):
    first = samplings[0]
    last = samplings[-1]

    def residuals(params, data):
        # params: [ctrl1.x, ctrl1.y, ctrl2.x, ctrl2.y, t1, t2, ..., tn-1]
        ctrls = params[:4].reshape(2, 2)
        t_values = np.clip(params[4:], 0, 1)  # force in [0,1]
        errors = []
        for t, (x, y) in zip(t_values, data):
            b = (1 - t)**3 * first + \
                3 * (1 - t)**2 * t * ctrls[0] + \
                3 * (1 - t) * t**2 * ctrls[1] + \
                t**3 * last
            errors.extend([b[0] - x, b[1] - y])
        return np.array(errors)
    
    init_t = np.linspace(0, 1, len(samplings))[1:-1] # initial t guess
    init_params = np.concatenate([init_ctrls.flatten(), init_t])

    ctrl_lower = [first[0], first[1] - math.pi, first[0], last[1] - math.pi]
    ctrl_upper = [last[0], first[1] + math.pi, last[0], last[1] + math.pi]
    bounds = (
        ctrl_lower + [-1] * len(samplings[1:-1]), # lower bound
        ctrl_upper + [1] * len(samplings[1:-1]), # upper bound
    )

    result = sci_optimize.least_squares(
        residuals, 
        init_params,
        bounds=bounds,
        args=(samplings[1:-1],),
        method='trf',
        max_nfev=10000 * len(init_params),
        ftol=1e-7,
        xtol=1e-7,
        gtol=1e-7,
    )
    if not result.success:
        raise Exception(f'Fitting failed. status={result.status} message={result.message}')
    optimized_ctrls = result.x[:4].reshape(2, 2)
    optimized_t = result.x[4:]
    print({
        'optimized_ctrls': [
            (optimized_ctrls[0][0], math.radians(optimized_ctrls[0][1])),
            (optimized_ctrls[1][0], math.radians(optimized_ctrls[1][1]))
        ],
        'optimized_t': optimized_t,
        'cost': result.cost,
        'optimality': result.optimality,
        'nfev': result.nfev,
        'njev': result.njev,
        'status': result.status
    })
    return (optimized_ctrls[0], optimized_ctrls[1])


apply_bezier_fitting()
