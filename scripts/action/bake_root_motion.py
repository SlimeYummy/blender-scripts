import bpy
from action_utils import find_fcurve_by_id


class RootMotionMeta:
    src_action: str
    dst_action: str
    sequences: list[tuple[int, int, str]]

    def __init__(self, src_action, dst_action, sequences):
        self.src_action = src_action
        self.dst_action = dst_action
        self.sequences = sequences


cfg_metas = [
    RootMotionMeta('Attack_01A_#edit2', 'Attack_01A', [
        (0, 17, 'c_foot_ik.r'),
        (18, 58, 'c_foot_ik.l'),
    ]),
    RootMotionMeta('Attack_02A_#edit2', 'Attack_02A', [
        (0, 17, 'c_foot_ik.r'),
        (18, 58, 'c_foot_ik.l'),
    ]),
    RootMotionMeta('Attack_03A_#edit2', 'Attack_03A', [
        (10, 46, 'c_foot_ik.r'),
    ]),
    RootMotionMeta('Attack_04A_#edit2', 'Attack_04A', [
        (22, 60, 'c_foot_ik.r'),
    ]),
]

print('====================================')

selected_objects = bpy.context.selected_objects
if not selected_objects or len(selected_objects) != 1:
    raise Exception('Must select 1 object')

dst_obj = selected_objects[0]
if not dst_obj.animation_data or not dst_obj.animation_data.action:
    raise Exception('Object must have an action')

dst_act = dst_obj.animation_data.action
meta = next(filter(lambda x: x.dst_action == dst_act.name, cfg_metas), None)
if not meta:
    raise Exception(f'Meta not found "{dst_act.name}"')

print('src action:', meta.src_action)
print('dst action:', meta.dst_action)
print('sequences:', meta.sequences)

src_act =  bpy.data.actions.get(meta.src_action)
if not src_act:
    raise Exception(f'Action "{meta.src_action}" not found')

dst_fcurve = find_fcurve_by_id(dst_act, 'pose.bones["Root"].location.z')
if dst_fcurve:
    dst_fcurve.keyframe_points.clear()
else:
    dst_fcurve = dst_act.fcurves.new('pose.bones["Root"].location', index=2, action_group='Root')

total_motion = 0
for start, finish, bone in meta.sequences:
    src_fcurve = find_fcurve_by_id(src_act, f'pose.bones["{bone}"].location.y')
    prev_val = src_fcurve.evaluate(start - 1)

    for frame in range(start, finish + 1):
        cur_val = src_fcurve.evaluate(frame)
        total_motion = total_motion - (cur_val - prev_val)
        prev_val = cur_val

        keyframe = dst_fcurve.keyframe_points.insert(frame, total_motion, options={'FAST'})
        keyframe.interpolation = 'LINEAR'
