bl_info = {
    "name": "Script Center",
    "author": "SlimeYummy",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > Script",
    "description": "Execute and manage your scripts in a simple way",
    "category": "Other",
}

import bpy
import os
import importlib.util


SCRIPT_PATH = os.path.normpath(f"{__file__}/../../../scripts")

FOLDERS = {
    '/general': 'General - ',
    '/action': 'Action - ',
    '/custom': 'Custom - ',
}

NO_RUNS = set([
    # 'imitate_action_curve'
])

class ScriptManager:
    scripts = None

    @classmethod
    def list_scripts(cls, refresh = False):
        cls.scripts: dict[str, str] = {}

        if cls.scripts and not refresh:
            return cls.scripts
        
        for folder, prefix in FOLDERS.items():
            path = SCRIPT_PATH + folder
            for file in os.listdir(path):
                if file.endswith(".py") and file not in cls.scripts:
                    name = prefix + file.replace(".py", "")
                    cls.scripts[name] = f"{path}/{file}"
        return cls.scripts
    
    @classmethod
    def run_script(cls, script):
        path = cls.scripts.get(script, None)
        if not path:
            raise Exception(f"Script {script} not found")
        spec = importlib.util.spec_from_file_location(script, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


class ScriptCenterMain(bpy.types.Panel):
    bl_label = "Script Center"
    bl_idname = "ScriptCenterMain"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Script"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("script_center.refresh", icon='FILE_SCRIPT', emboss=True)
        row.operator("script.reload", icon='FILE_REFRESH', emboss=True)

        column = layout.column(align=True)

        for script in ScriptManager.list_scripts():
            row = column.box().row(align=True)
            row.label(text=script)
            row.scale_x = 3

            col1 = row.column(align=True)
            col1.enabled = not script in NO_RUNS
            run = col1.operator("script_center.run", text='', icon='PLAY')
            run.script = script
            
            # col2 = row.column(align=True)
            # col2.operator("script_center.run", text='', icon='TEXT')


class ScriptCenterRefresh(bpy.types.Operator):
    bl_idname = "script_center.refresh"
    bl_label = "Refresh files"
    bl_description = "Refresh files"

    def execute(self, context):
        ScriptManager.list_scripts(True)
        return {'FINISHED'}

# bpy.ops.script.reload()
class ScriptCenterRun(bpy.types.Operator):
    bl_idname = "script_center.run"
    bl_label = "Run script"
    bl_description = "Run script"
    
    script: bpy.props.StringProperty()

    def execute(self, context):
        ScriptManager.run_script(self.script)
        self.report({'INFO'}, f"{self.script} executed successfully")
        return {'FINISHED'}

    def draw(self, context):
        self.layout.label(text=self.script, alignment='LEFT')


classes = (ScriptCenterMain, ScriptCenterRefresh, ScriptCenterRun)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
