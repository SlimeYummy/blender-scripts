from action_utils import get_selected_fcurves


selected_fcurves = get_selected_fcurves()

if len(selected_fcurves) != 2:
    raise Exception('Must select 2 fcurves')

if selected_fcurves[0].data_path != selected_fcurves[1].data_path:
    raise Exception('Fcurves must have the same data path')

data_path = selected_fcurves[0].data_path
data_index = selected_fcurves[0].array_index
color = selected_fcurves[0].color
color_mode = selected_fcurves[0].color_mode

selected_fcurves[0].data_path = selected_fcurves[1].data_path
selected_fcurves[0].array_index = selected_fcurves[1].array_index
selected_fcurves[0].color = color
selected_fcurves[0].color_mode = color_mode

selected_fcurves[1].data_path = data_path
selected_fcurves[1].array_index = data_index
selected_fcurves[1].color = color
selected_fcurves[1].color_mode = color_mode
