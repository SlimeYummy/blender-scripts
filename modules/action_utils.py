import bpy
import math
import re

from typing import Callable


def make_fcurve_id(fcurve: bpy.types.FCurve) -> str:
    match fcurve.array_index:
        case 0: return f"{fcurve.data_path}.x"
        case 1: return f"{fcurve.data_path}.y"
        case 2: return f"{fcurve.data_path}.z"
        case 3: return f"{fcurve.data_path}.w"
        case _: raise Exception("Unexpected array index")


def parse_fcurves_array_index(id: str) -> int:
    match id[-2:]:
        case ".x": return 0
        case ".y": return 1
        case ".z": return 2
        case ".w": return 3
        case _: raise Exception("Unexpected id")


def action_frame_range(action):
    start = math.floor(action.frame_range[0])
    stop = math.ceil(action.frame_range[1])
    return range(start, stop + 1)


def travel_action_fcurves(
    action: bpy.types.Action | None,
    callback: Callable[bpy.types.FCurve, bool | None],
    *,
    re_include: re.Pattern | None = None,
    re_exclude: re.Pattern | None = None,
    location: bool = False,
    euler: bool = False,
    quaternion: bool = False,
    scale: bool = False
):
    action = action or bpy.context.view_layer.objects.active.animation_data.action
    for fcurve in action.fcurves:
        if re_include and not re_include.match(fcurve.data_path):
            continue
        if re_exclude and re_exclude.match(fcurve.data_path):
            continue

        if fcurve.data_path.endswith('.location'):
            if location:
                if callback(fcurve):
                    return
        elif fcurve.data_path.endswith('.rotation_euler'):
            if euler:
                if callback(fcurve):
                    return
        elif fcurve.data_path.endswith('.rotation_quaternion'):
            if quaternion:
                if callback(fcurve):
                    return
        elif fcurve.data_path.endswith('.scale'):
            if scale:
                if callback(fcurve):
                    return


def find_fcurve_by_id(
    action: bpy.types.Action,
    fcurve_id: str
):
    for fcurve in action.fcurves:
        if make_fcurve_id(fcurve) == fcurve_id:
            return fcurve
    return None


def get_selected_fcurves():
    fcurves = None
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'GRAPH_EDITOR':
                with bpy.context.temp_override(window=window, area=area):
                    fcurves = bpy.context.selected_visible_fcurves
                break
    if fcurves is None or len(fcurves) == 0:
        raise Exception('No fcurves selected')
    
    selected_fcurves = []
    for fc in fcurves:
        if fc.lock or fc.hide:
            continue
        selected_fcurves.append(fc)
    if len(selected_fcurves) == 0:
        raise Exception('No fcurve selected')
    return selected_fcurves


def get_selected_fcurve():
    fcurves = get_selected_fcurves()
    if len(fcurves) > 1:
        raise Exception('Multiple fcurves selected')
    return fcurves


def search_fcurve(
    fcurve: bpy.types.FCurve,
    callback: Callable[bpy.types.Keyframe, bool | None]
):
    for keyframe in fcurve.keyframe_points:
        if callback(keyframe):
            return keyframe
    return None
