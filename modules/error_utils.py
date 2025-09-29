import bpy
import traceback

from typing import Callable


def protect_call(func: Callable):
    try:
        func()
    except Exception as e:
        traceback.print_exc()
        def draw_error(self, context):
            for line in traceback.format_exc().split('\n')[:-1]:
                self.layout.row().label(text=line)
        bpy.context.window_manager.popup_menu(draw_error, title="Error", icon='ERROR')
