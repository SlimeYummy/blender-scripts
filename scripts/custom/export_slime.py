import bpy
import bmesh
import math
import mathutils
import re
import json
import pathlib


def prepare_target_action(current_action, new_name=None):
    # 检查后缀是否为 _raw
    current_name = current_action.name
    if not current_name.endswith("_raw"):
        raise Exception(f"No '_raw' suffix. current_action='{current_name}'")

    # 建新或清空 action
    new_action_name = new_name or current_name[:-len("_raw")]
    target_action = bpy.data.actions.get(new_action_name)
    if target_action:
        for fcurve in list(target_action.fcurves):
            target_action.fcurves.remove(fcurve)
    else:
        target_action = bpy.data.actions.new(name=new_action_name)
    
    if len(target_action.slots) == 0:
        target_action.slots.new('OBJECT', 'Armature')

    return target_action


def collect_bones(active_obj, root_name, include_root=True):
    if active_obj.type != 'ARMATURE':
        raise Exception(f"Active object not an Armature. active_obj='{active_obj.name}'")
    
    root_bone = active_obj.data.bones.get(root_name)
    if not root_bone:
        raise Exception(f"Root bone not found. root_name='{root_name}'")

    if include_root:
        return [root_bone, *root_bone.children_recursive]
    else:
        return list(root_bone.children_recursive)


def sample_action(current_action, target_action, bones, frame_range=None):
    bone_names = {bone.name for bone in bones}
    if frame_range:
        frame_start = int(frame_range[0])
        frame_end = int(frame_range[1])
    else:
        frame_start = int(current_action.frame_range[0])
        frame_end = int(current_action.frame_range[1])
    
    for src_fcurve in current_action.fcurves:
        # 提取 pose.bones["BoneName"] 中的 BoneName
        data_path = src_fcurve.data_path
        match = re.match(r'pose\.bones\["([^"]+)"\]', data_path)
        if not match:
            continue

        # 只有属于 bones 的才处理
        bone_name = match.group(1)
        if bone_name not in bone_names:
            continue

        # 保留原有的 group 没有则使用骨骼名
        group_name = src_fcurve.group.name if src_fcurve.group else bone_name
        new_fcurve = target_action.fcurves.new(
            data_path=data_path,
            index=src_fcurve.array_index,
            action_group=group_name
        )
        
        # 批量添加 keyframes 提高效率
        num_frames = (frame_end - frame_start) * 2 + 1
        if num_frames > 0:
            new_fcurve.keyframe_points.add(num_frames)
            
            for idx in range(num_frames):
                val = src_fcurve.evaluate(frame_start + idx * 0.5)
                kf = new_fcurve.keyframe_points[idx]
                kf.co = (idx * 0.5, val)
                kf.interpolation = 'LINEAR'
            
            new_fcurve.update()


def make_root_motion_z_zeroed(target_action, root_name):
    # 找到 root 的 fcurve
    root_fcurve = None

    for fc in target_action.fcurves:
        if fc.array_index == 2:
            if fc.data_path == f'pose.bones["{root_name}"].location':
                root_fcurve = fc
                break

    if not root_fcurve:
        raise Exception(f"Bone not found. root_name='{root_name}'")

    # 初始值不为0 则所有帧偏移该差值
    if len(root_fcurve.keyframe_points) > 0:
        z_offset = root_fcurve.keyframe_points[0].co[1]
        
        if abs(z_offset) != 0:
            for kf in root_fcurve.keyframe_points:
                frame, val = kf.co
                kf.co = (frame, val - z_offset)
                
            root_fcurve.update()


def make_root_motion_y_positive(target_action, root_name, body_name):
    # 找到 root 和 body 的 fcurve
    root_fcurve = None
    body_fcurve = None

    for fc in target_action.fcurves:
        if fc.array_index == 1:
            if fc.data_path == f'pose.bones["{root_name}"].location':
                root_fcurve = fc
            elif fc.data_path == f'pose.bones["{body_name}"].location':
                body_fcurve = fc

    if not root_fcurve:
        raise Exception(f"Bone not found. root_name='{root_name}'")
    if not body_fcurve:
        raise Exception(f"Bone not found. body_name='{body_name}'")

    if len(root_fcurve.keyframe_points) != len(body_fcurve.keyframe_points):
        raise Exception(f"Keyframe points length mismatch. root_name='{root_name}', body_name='{body_name}'")

    # 将 root 的负值移动到 body 上
    for idx in range(len(root_fcurve.keyframe_points)):
        root_kf = root_fcurve.keyframe_points[idx]
        body_kf = body_fcurve.keyframe_points[idx]
        
        root_frame, root_val = root_kf.co
        body_frame, body_val = body_kf.co
        
        if round(root_frame, 3) != round(body_frame, 3):
            raise Exception(
                f"Frame mismatch at index {idx}. "
                f"root_name='{root_name}', root_frame={root_frame}, "
                f"body_name='{body_name}', body_frame={body_frame}"
            )

        if root_val < 0:
            diff = root_val
            root_kf.co = (root_frame, 0.0)
            body_kf.co = (body_frame, body_val + diff)

    root_fcurve.update()
    body_fcurve.update()


def export_shape_keys(path, current_action, bones, frame_range=None):
    bone_names = {bone.name for bone in bones}
    
    if frame_range:
        frame_start = int(frame_range[0])
        frame_end = int(frame_range[1])
    else:
        frame_start = int(current_action.frame_range[0])
        frame_end = int(current_action.frame_range[1])

    fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
    duration = (frame_end - frame_start) / fps

    results = []
    for src_fcurve in current_action.fcurves:
        # 只取 location.y (array_index == 1)
        if src_fcurve.array_index != 1:
            continue

        # 提取 pose.bones["BoneName"] 中的 BoneName
        data_path = src_fcurve.data_path
        match = re.match(r'pose\.bones\["([^"]+)"\]\.location', data_path)
        if not match:
            continue

        # 只有属于 bones 的才处理
        bone_name = match.group(1)
        if bone_name not in bone_names:
            continue

        # 合成 JSON
        json_data = []
        num_frames = (frame_end - frame_start) * 2 + 1
        for idx in range(num_frames):
            frame = idx * 0.5
            val = src_fcurve.evaluate(frame_start + frame)
            json_data.append({
                "t": frame / fps,
                "v": val
            })

        results.append({
            "name": bone_name,
            "type": "float1",
            "duration": duration,
            "data": json_data
        })
        
    if results:
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=2)


ACTIONS = {
    'Walk_Front_raw': {
        'WalkFrontStart': (0, 20),
        'WalkFrontLoop': (20, 60),
        'WalkFrontStop': (60, 80),
    },
    'Walk_Back_raw': {
        'WalkBackStart': (0, 20),
        'WalkBackLoop': (20, 60),
        'WalkBackStop': (60, 80),
    },
    'Walk_Left_raw': {
        'WalkLeftStart': (0, 20),
        'WalkLeftLoop': (20, 60),
        'WalkLeftStop': (60, 80),
    },
    'Walk_Right_raw': {
        'WalkRightStart': (0, 20),
        'WalkRightLoop': (20, 60),
        'WalkRightStop': (60, 80),
    },
    'Run_raw': {
        'RunStart': (0, 25),
        'RunLoop': (25, 45),
        'RunStop': (65, 93),
    },
    'Attack1A_raw': { 'Attack1A': (0, 84) },
    'Dodge_F_raw': { 'Dodge_F': (0, 55) },
    'Dodge_B_raw': { 'Dodge_B': (0, 55) },
    'Dodge_L_raw': { 'Dodge_L': (0, 55) },
    'Dodge_R_raw': { 'Dodge_R': (0, 55) },
    'BeHit1_B_raw': { 'BeHit1_B': (0, 60) },
    'BeHit1_F_raw': { 'BeHit1_F': (0, 60) },
    'BeHit1_L_raw': { 'BeHit1_L': (0, 60) },
    'BeHit1_R_raw': { 'BeHit1_R': (0, 60) },
}


def main():
    print('======================================')

    context = bpy.context
    active_obj = context.active_object

    if not active_obj:
        raise Exception("No active object selected.")
    print(f"Current active object: {active_obj.name}")
    
    action = active_obj.animation_data and active_obj.animation_data.action
    if not action:
        raise Exception(f"Action not found. active_obj='{active_obj.name}'")
    
    if action.name in ACTIONS:
        for new_name, frame_range in ACTIONS[action.name].items():
            handle_action(active_obj, action, new_name, frame_range)
    else:
        handle_action(active_obj, action)

def handle_action(active_obj, current_action, new_name=None, new_range=None):
    target_action = prepare_target_action(current_action, new_name=new_name)
    print(f"Current action: '{current_action.name}'")
    print(f"Target action: '{target_action.name}'")

    skeletal_bones = collect_bones(active_obj, "Root", include_root=True)
    print(f"Skeletal bones: {[bone.name for bone in skeletal_bones]}")
    sample_action(current_action, target_action, skeletal_bones, frame_range=new_range)
    print(f"Sample action done.")

    make_root_motion_y_positive(target_action, "Root", "Body")
    print(f"Make root motion y positive done.")

    make_root_motion_z_zeroed(target_action, "Root")
    print(f"Make root motion z zeroed done.")
    
    shape_key_bones = collect_bones(active_obj, "ShapeKeys", include_root=False)
    print(f"Shape key bones: {[bone.name for bone in shape_key_bones]}")
    shape_key_name = new_name or target_action.name
    path = f"D:/project/G1/PointAssets/Slime/{shape_key_name}.sk-json"
    export_shape_keys(path, current_action, shape_key_bones, frame_range=new_range)
    print(f"Export shape keys done. path='{path}'")

main()
