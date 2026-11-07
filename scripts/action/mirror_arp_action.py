"""Mirror the ARP rig's current action with Blender's Paste Flipped.

- Source action: whatever is active on ARP_RIG_NAME.
- New action: source name + "_MIRROR" (rename it afterwards if needed).
- Both weapon armatures are forced onto the same source action before mirroring.
- Weapon_0_Root / Weapon_1_Root / WeaponControl_* curves on the ARP rig are skipped.
- HandR/HandL location offsets in the weapon slots are swapped after the flip.
- The Action Editor must be open in "Action" mode.
- The script never saves the .blend.
"""

import re

import bpy


ARP_RIG_NAME = 'rig_old'

WEAPON_NAME = ('AxeArmatureFK', 'AxeArmature')
WEAPON_SLOT = ('WeaponFK', 'Weapon')
WEAPON_IK_NAME = ('AxeArmatureIK',)
WEAPON_IK_SLOT = ('WeaponIK',)

# Curves for these ARP bones are copied as-is instead of being flipped.
SKIP_BONE_PREFIXES = (
    'Weapon_0_Root',
    'Weapon_1_Root',
    'WeaponControl_',
)

# HandR/HandL are mirrored by mirror_weapon_hands(), not by Paste Flipped.
WEAPON_HANDS = ('HandR', 'HandL')


RE_BONE_PATH = re.compile(r'^pose\.bones\["([^"]+)"\]\.')


def find_action_editor():
    for area in bpy.context.screen.areas:
        if area.type != 'DOPESHEET_EDITOR':
            continue
        if area.spaces.active.mode != 'ACTION':
            continue
        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        if region is not None:
            return area, region
    raise RuntimeError(
        'No Action Editor found. Open a Dope Sheet in Action mode and run again.')


def find_channelbag(action, slot):
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in strip.channelbags:
                if channelbag.slot and channelbag.slot.identifier == slot.identifier:
                    return channelbag
    return None


def assign_action(obj, action, source_slot):
    target_slot = next(
        (s for s in action.slots if s.identifier == source_slot.identifier), None)
    if target_slot is None:
        raise RuntimeError(
            f'Action "{action.name}" has no slot "{source_slot.identifier}"')
    if obj.animation_data is None:
        obj.animation_data_create()
    obj.animation_data.action = action
    obj.animation_data.action_slot = target_slot
    action.slots.active = target_slot
    return target_slot


def is_skipped(data_path):
    match = RE_BONE_PATH.match(data_path)
    if match is None:
        return False
    bone_name = match.group(1)
    return any(bone_name.startswith(p) for p in SKIP_BONE_PREFIXES)


def is_weapon_hand_location(data_path):
    match = RE_BONE_PATH.match(data_path)
    if match is None:
        return False
    return (match.group(1) in WEAPON_HANDS
            and data_path.endswith('.location'))


def mirror_slot(area, region, obj, action, source_slot):
    assign_action(obj, action, source_slot)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()

    channelbag = find_channelbag(action, source_slot)
    if channelbag is None or not channelbag.fcurves:
        print(f'  slot {source_slot.identifier:12s} : empty, skipped')
        return

    curve_count = len(channelbag.fcurves)
    key_count = sum(len(fc.keyframe_points) for fc in channelbag.fcurves)

    with bpy.context.temp_override(
        area=area,
        region=region,
        object=obj,
        active_object=obj,
        selected_objects=[obj],
    ):
        bpy.ops.action.select_all(action='SELECT')

        skipped_weapon = 0
        skipped_hand = 0
        for fcurve in channelbag.fcurves:
            if is_skipped(fcurve.data_path):
                skipped_weapon += 1
            elif is_weapon_hand_location(fcurve.data_path):
                skipped_hand += 1
            else:
                continue
            fcurve.select = False
            for key in fcurve.keyframe_points:
                key.select_control_point = False
                key.select_left_handle = False
                key.select_right_handle = False

        bpy.ops.action.copy()
        result = bpy.ops.action.paste(
            flipped=True, merge='OVER_ALL', offset='NONE')
        if result != {'FINISHED'}:
            raise RuntimeError(
                f'Paste Flipped failed on slot "{source_slot.identifier}" ({result})')

    kept = []
    if skipped_weapon:
        kept.append(f'{skipped_weapon} weapon curves')
    if skipped_hand:
        kept.append(f'{skipped_hand} hand curves')
    kept_text = ' + '.join(kept)
    print(f'  slot {source_slot.identifier:12s} : {obj.name:16s} '
          f'{curve_count} curves / {key_count} keys'
          + (f' ({kept_text} kept)' if kept_text else ''))


def find_hand_curves(channelbag, hand_name):
    prefix = f'pose.bones["{hand_name}"].location'
    return {fc.array_index: fc for fc in channelbag.fcurves
            if fc.data_path == prefix}


def mirror_weapon_hands(armature, source_action, target_action, source_slot):
    """Swap HandR/HandL locations in a weapon slot, mirrored across X.

    The bones' rest heads are offset along local Z, so swapping their world
    positions needs the rest distance added/subtracted after the XY swap.
    """
    source_bag = find_channelbag(source_action, source_slot)
    target_bag = find_channelbag(target_action, source_slot)
    if source_bag is None or target_bag is None:
        return

    source_curves = {name: find_hand_curves(source_bag, name)
                     for name in WEAPON_HANDS}
    if any(len(curves) != 3 for curves in source_curves.values()):
        return

    hand_r = armature.data.bones.get('HandR')
    hand_l = armature.data.bones.get('HandL')
    if hand_r is None or hand_l is None:
        return
    axis = hand_r.matrix_local.to_3x3().col[2]
    distance = (hand_r.head_local - hand_l.head_local).dot(axis)
    if distance <= 0:
        raise RuntimeError('HandR must be ahead of HandL along local Z')

    target_curves = {}
    for hand_name in WEAPON_HANDS:
        curves = find_hand_curves(target_bag, hand_name)
        prefix = f'pose.bones["{hand_name}"].location'
        for index in range(3):
            if index in curves:
                continue
            source_curve = source_curves[hand_name][index]
            group_name = (source_curve.group.name
                          if source_curve.group else hand_name)
            curves[index] = target_bag.fcurves.new(
                prefix, index=index, group_name=group_name)
        target_curves[hand_name] = curves

    frames = set()
    for curves in (source_curves, target_curves):
        for hand_curves in curves.values():
            for fcurve in hand_curves.values():
                frames.update(key.co[0] for key in fcurve.keyframe_points)

    for frame in sorted(frames):
        source_hand_r = [source_curves['HandR'][i].evaluate(frame)
                         for i in range(3)]
        source_hand_l = [source_curves['HandL'][i].evaluate(frame)
                         for i in range(3)]
        values = {
            'HandR': (-source_hand_l[0], source_hand_l[1],
                      source_hand_l[2] - distance),
            'HandL': (-source_hand_r[0], source_hand_r[1],
                      source_hand_r[2] + distance),
        }
        for hand_name, hand_values in values.items():
            for index, value in enumerate(hand_values):
                fcurve = target_curves[hand_name][index]
                key = next(
                    (k for k in fcurve.keyframe_points
                     if abs(k.co[0] - frame) < 1e-4), None)
                if key is None:
                    key = fcurve.keyframe_points.insert(frame, value)
                else:
                    key.co[1] = value
                fcurve.update()

    print(f'  hands {source_slot.name_display:12s} : HandR/HandL swapped '
          f'(d={distance:.4f})')


def main():
    print('==== MIRROR ARP ACTION ====')

    rig = bpy.data.objects.get(ARP_RIG_NAME)
    if rig is None or rig.type != 'ARMATURE':
        raise RuntimeError(f'ARP rig "{ARP_RIG_NAME}" not found')
    if rig.animation_data is None or rig.animation_data.action is None:
        raise RuntimeError(f'ARP rig "{ARP_RIG_NAME}" has no active action')
    if rig.animation_data.action_slot is None:
        raise RuntimeError(f'ARP rig "{ARP_RIG_NAME}" has no active action slot')

    source = rig.animation_data.action
    participants = [(rig, rig.animation_data.action_slot)]

    for names, slot_names in (
        (WEAPON_NAME, WEAPON_SLOT),
        (WEAPON_IK_NAME, WEAPON_IK_SLOT),
    ):
        obj = None
        for n in names:
            cand = bpy.data.objects.get(n)
            if cand is not None:
                obj = cand
                break
        if obj is None or obj.type != 'ARMATURE':
            raise RuntimeError(f'Weapon armature {names} not found')
        slot = None
        for sn in slot_names:
            slot = next(
                (s for s in source.slots if s.name_display == sn), None)
            if slot is not None:
                break
        if slot is None:
            raise RuntimeError(
                f'Action "{source.name}" has no slot {slot_names}')
        participants.append((obj, slot))

    target = source.copy()
    target.name = source.name + '--MIRROR'

    area, region = find_action_editor()
    dope_sheet = area.spaces.active.dopesheet
    dope_sheet.show_only_slot_of_active_object = True
    dope_sheet.show_only_selected = False

    try:
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        print(f'source: {source.name}')
        print(f'target: {target.name}')

        # Force the weapon armatures onto the ARP rig's current action.
        for obj, slot in participants[1:]:
            assign_action(obj, source, slot)
            print(f'forced {obj.name} -> {source.name} ({slot.identifier})')

        for obj, slot in participants:
            mirror_slot(area, region, obj, target, slot)

        for obj, slot in participants[1:]:
            mirror_weapon_hands(obj, source, target, slot)

        for obj, slot in participants:
            assign_action(obj, target, slot)
        print('assigned target action to: '
              + ', '.join(obj.name for obj, _ in participants))
        print(f'==== DONE: "{target.name}" ====')
    finally:
        dope_sheet.show_only_slot_of_active_object = False
        dope_sheet.show_only_selected = False


main()
