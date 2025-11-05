import math
import bpy
import importlib
import json
import pathlib
import re
import custom_utils as cu

importlib.reload(cu)

# start_frame = 0
# finish_frame = 46
# duration = (finish_frame - start_frame) / 60

print('======================================')

re_action = re.compile(r"Axe_(\w+)(_edit|_bake|_pre)\d?")

waepon_obj = bpy.data.objects.get('AxeArmature')
waepon_joint = waepon_obj.pose.bones.get('Root')
action = waepon_obj.animation_data.action

match = re_action.match(action.name)
if not match:
    raise Exception(f'Invalid action name "{action.name}"')
out_name = match.group(1)

meta = cu.find_action_meta(out_name)

json_pos = [] # model space
json_rot = [] # model space

saved_frame = bpy.context.scene.frame_current
for raw_frame in range(meta.raw_start, meta.raw_finish + 1):
    frame = meta.frame_map.get(raw_frame)
    if not frame:
        continue
    bpy.context.scene.frame_set(raw_frame)

    p = waepon_joint.matrix.translation
    json_pos.append({
        "t": frame / 60,
        "v": [p.x, p.z, -p.y]
    })

    r = waepon_joint.matrix.to_quaternion()
    json_rot.append({
        "t": frame / 60,
        "v": [r.x, r.z, -r.y, r.w]
    })
bpy.context.scene.frame_set(saved_frame)

path = f"D:/project/G1/PointAssets/Animations/GirlAttack/{out_name}.json"
pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
print(path)
print(meta.frame_map)

with open(path, "w", encoding="utf-8") as file:
    duration = meta.duration / 60
    json.dump([
        { "name": "Pos:Axe", "type": "float3", "duration": duration, "data": json_pos},
        { "name": "Rot:Axe", "type": "quaternion", "duration": duration, "data": json_rot},
    ], file, ensure_ascii=False, indent=2)
