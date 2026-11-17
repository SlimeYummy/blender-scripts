import math
import os
import re
from time import sleep
import bpy
import json
import pathlib
from mathutils import Vector
from action_utils import find_fcurves_by_ids

BONES = ['c_leg_pole.l', 'c_leg_pole.r']

OUT_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'Girl')


def collect_frame_points(left_fcurves, right_fcurves):
    frame_points = {}
    for fcurves, bone_name in ((left_fcurves, 'c_leg_pole.l'), (right_fcurves, 'c_leg_pole.r')):
        for fcu in fcurves:
            for kp in fcu.keyframe_points:
                frame = kp.co.x
                bones = frame_points.setdefault(frame, [])
                if bone_name not in bones:
                    bones.append(bone_name)
    return frame_points


def save_pole_location(action):
    # Step1: collect keyframe time points

    left_fcurves = find_fcurves_by_ids(action, [
        'pose.bones["c_leg_pole.l"].location.x',
        'pose.bones["c_leg_pole.l"].location.y',
        'pose.bones["c_leg_pole.l"].location.z',
    ])
    if len(left_fcurves) < 3:
        raise Exception(f'Armature="{obj.name}" has no location fcurves')

    right_fcurves = find_fcurves_by_ids(action, [
        'pose.bones["c_leg_pole.r"].location.x',
        'pose.bones["c_leg_pole.r"].location.y',
        'pose.bones["c_leg_pole.r"].location.z',
    ])
    if len(right_fcurves) < 3:
        raise Exception(f'Armature="{obj.name}" has no location fcurves')

    frame_points = collect_frame_points(left_fcurves, right_fcurves)

    # Step2: sample world-space positions

    left_data = {}
    right_data = {}

    def sample_frame(f, bones):
        bpy.context.scene.frame_set(f)
        out = {}
        for bone_name in bones:
            pos = (obj.matrix_world @ obj.pose.bones[bone_name].matrix).translation
            out[bone_name] = pos.copy()
        return out

    saved_frame = bpy.context.scene.frame_current
    try:
        for frame, bones in frame_points.items():
            frame_int = round(frame)
            if frame == frame_int:
                positions = sample_frame(frame_int, bones)
            else:
                f0 = math.floor(frame)
                f1 = math.ceil(frame)
                p0 = sample_frame(f0, bones)
                p1 = sample_frame(f1, bones)
                positions = {bone_name: p0[bone_name].lerp(p1[bone_name], frame - f0) for bone_name in bones}
            for bone_name, pos in positions.items():
                data = left_data if bone_name == 'c_leg_pole.l' else right_data
                data[str(frame)] = [pos.x, pos.y, pos.z]
    finally:
        bpy.context.scene.frame_set(saved_frame)

    # Step3: save to json

    path = f'{OUT_DIR}/{action.name}_pole.json'
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        json.dump({
            'action': action.name,
            'armature': obj.name,
            'c_leg_pole.l': left_data,
            'c_leg_pole.r': right_data,
        }, file, ensure_ascii=False, indent=2)

    print(f"{action.name} => {path}")


def load_pole_location(action):
    # Step1: load from json

    path = f'{OUT_DIR}/{action.name}_pole.json'
    if not pathlib.Path(path).exists():
        raise Exception(f'File not found: {path}')
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    left_data = data['c_leg_pole.l']
    right_data = data['c_leg_pole.r']

    # Step2: collect fcurves

    left_fcurves = find_fcurves_by_ids(action, [
        'pose.bones["c_leg_pole.l"].location.x',
        'pose.bones["c_leg_pole.l"].location.y',
        'pose.bones["c_leg_pole.l"].location.z',
    ])
    if len(left_fcurves) < 3:
        raise Exception(f'Armature="{obj.name}" has no location fcurves')

    right_fcurves = find_fcurves_by_ids(action, [
        'pose.bones["c_leg_pole.r"].location.x',
        'pose.bones["c_leg_pole.r"].location.y',
        'pose.bones["c_leg_pole.r"].location.z',
    ])
    if len(right_fcurves) < 3:
        raise Exception(f'Armature="{obj.name}" has no location fcurves')

    # Step3: reverse-derive pose-space locations and overwrite existing keyframes

    def apply_positions(bone, fcurves, data):
        kp_maps = [{kp.co.x: kp for kp in fcu.keyframe_points} for fcu in fcurves]
        A = obj.matrix_world
        for frame_str, world in data.items():
            frame = float(frame_str)
            world_m = (A @ bone.matrix).copy()
            world_m.translation = Vector(world)
            bone.matrix = A.inverted() @ world_m
            loc = bone.location
            for axis, kp_map in enumerate(kp_maps):
                kp = kp_map.get(frame)
                if kp is None:
                    continue
                kp.co[1] = loc[axis]
        for fcu in fcurves:
            kps = sorted(fcu.keyframe_points, key=lambda kp: kp.co.x)
            idxs = set()
            for i, kp in enumerate(kps):
                if kp.interpolation == 'BEZIER' and kp.type != 'BREAKDOWN':
                    idxs.add(i)
                    idxs.add(i + 1)
            for i in idxs:
                if i < len(kps):
                    kp = kps[i]
                    kp.handle_left_type = 'AUTO'
                    kp.handle_right_type = 'AUTO'
            fcu.update()

    apply_positions(obj.pose.bones['c_leg_pole.l'], left_fcurves, left_data)
    apply_positions(obj.pose.bones['c_leg_pole.r'], right_fcurves, right_data)

    print(f"{action.name} <= {path}")


print('====================================')

RE_ACTION = re.compile(r'^Attack\w+_#\w+$')

obj = bpy.context.view_layer.objects.active
if obj is None or obj.type != 'ARMATURE':
    raise Exception(f'Active object="{obj.name}" is not an armature')

# if obj.animation_data is None or obj.animation_data.action is None:
#     raise Exception(f'Armature="{obj.name}" has no active action')
# action = obj.animation_data.action

# load_pole_location(action)

saved_action = obj.animation_data.action
for action in bpy.data.actions:
    if not RE_ACTION.match(action.name):
        continue
    obj.animation_data.action = action
    load_pole_location(action)
