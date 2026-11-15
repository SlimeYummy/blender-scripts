import bpy
from action_utils import find_fcurve_by_id, new_fcurve

active_action = bpy.context.view_layer.objects.active.animation_data.action

X = False
Y = True
Z = False

if X and not find_fcurve_by_id(active_action, 'Raw.x'):
    new_fcurve(active_action, 'c_pos', 'Raw', 0)
if Y and not find_fcurve_by_id(active_action, 'Raw.y'):
    new_fcurve(active_action, 'c_pos', 'Raw', 1)
if Z and not find_fcurve_by_id(active_action, 'Raw.z'):
    new_fcurve(active_action, 'c_pos', 'Raw', 2)

if X and not find_fcurve_by_id(active_action, 'Default.x'):
    new_fcurve(active_action, 'c_pos', 'Default', 0)
if Y and not find_fcurve_by_id(active_action, 'Default.y'):
    new_fcurve(active_action, 'c_pos', 'Default', 1)
if Z and not find_fcurve_by_id(active_action, 'Default.z'):
    new_fcurve(active_action, 'c_pos', 'Default', 2)

if X and not find_fcurve_by_id(active_action, 'Move.x'):
    new_fcurve(active_action, 'c_pos', 'Move', 0)
if Y and not find_fcurve_by_id(active_action, 'Move.y'):
    new_fcurve(active_action, 'c_pos', 'Move', 1)
if Z and not find_fcurve_by_id(active_action, 'Move.z'):
    new_fcurve(active_action, 'c_pos', 'Move', 2)

if X and not find_fcurve_by_id(active_action, 'MoveEx.x'):
    new_fcurve(active_action, 'c_pos', 'MoveEx', 0)
if Y and not find_fcurve_by_id(active_action, 'MoveEx.y'):
    new_fcurve(active_action, 'c_pos', 'MoveEx', 1)
if Z and not find_fcurve_by_id(active_action, 'MoveEx.z'):
    new_fcurve(active_action, 'c_pos', 'MoveEx', 2)
