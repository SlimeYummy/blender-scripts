import math
import bpy
import importlib
import json
import pathlib
import re
from action_utils import find_fcurve_by_id
import custom_utils as cu

importlib.reload(cu)

print('======================================')

fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base

re_action = re.compile(r"(\w+)(_\#edit|_\#bake|_\#pre)\d?")

chara_obj = bpy.data.objects.get('rig_old') or bpy.data.objects.get('Armature')
action = chara_obj.animation_data.action
# if chara_obj.name == 'rig':
#     chara_joint = chara_obj.pose.bones.get('c_pos')
# else:
#     chara_joint = chara_obj.pose.bones.get('Root')

if chara_obj.name == 'rig' or chara_obj.name == 'rig_old':
    match = re_action.match(action.name)
    if not match:
        raise Exception(f'Invalid action name "{action.name}"')
    out_name = match.group(1)
else:
    out_name = action.name

meta = cu.find_action_meta(out_name)

def sample_position(name):
    pos = []

    fx = find_fcurve_by_id(action, f'{name}.x')
    fy = find_fcurve_by_id(action, f'{name}.y')
    fz = find_fcurve_by_id(action, f'{name}.z')
    if not fx and not fy and not fz:
        return None
        
    for raw_frame in range(meta.raw_start, meta.raw_finish + 1):
        frame = meta.frame_map.get(raw_frame)
        if not frame:
            continue

        x = fx.evaluate(frame) if fx else 0
        y = fy.evaluate(frame) if fy else 0
        z = fz.evaluate(frame) if fx else 0
        pos.append({
            "t": frame / fps,
            "v": [-x, z, y]
        })
    return pos

def default_rotation():
    return [
        { "t": 0, "v": [0, 0, 0, 1] },
        { "t": meta.duration / fps, "v": [0, 0, 0, 1] },
    ]


json_default = sample_position('Default')
json_move = sample_position('Move')
json_move_ex = sample_position('MoveEx')
json_rot = default_rotation()

if chara_obj.name == 'rig_old':
    path = f"D:/project/G1/PointAssets/Girl/{out_name}.rm-json"
else:
    path = f"D:/project/G1/PointAssets/TrainingDummy/{out_name}.rm-json"
pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
print(path)
# print(meta.frame_map)

with open(path, "w", encoding="utf-8") as file:
    duration = meta.duration / fps
    json.dump([
        { "name": "Pos:Default", "type": "float3", "duration": duration, "data": json_default},
        { "name": "Pos:Move", "type": "float3", "duration": duration, "data": json_move},
        { "name": "Pos:MoveEx", "type": "float3", "duration": duration, "data": json_move_ex},
        { "name": "Rot:Default", "type": "quaternion", "duration": duration, "data": json_rot},
    ], file, ensure_ascii=False, indent=2)
