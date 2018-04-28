import bpy

bl_info = {
    "name": "Robot Compiler",
    "description": "Robotics codesign and fabrication tool",
    "author": "UCLA LEMUR",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Properties > Measure",
    "warning": "", 
    "wiki_url": "",
    "tracker_url": "",
    "support": "TESTING",
    "category": "Object",
}

class RobotCompilerScreen(bpy.types.Operator):
    bl_idname = "robot_compiler.screen"        # unique identifier for buttons and menu items to reference.
    bl_label = "Add Robot Compiler Screen"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    # Adapted from https://blender.stackexchange.com/questions/63647/graphical-errors-while-changing-area-type-after-creating-a-new-screen/71646
    def delete_areas(self):
        override = bpy.context.copy()
        new = bpy.ops.screen.new()
        bpy.context.screen.name = "Robot Compiler"
        
        areas = []
        for i in override['screen'].areas:
            areas.append({'x': i.x, 'y': i.y, 'width': i.width, 'height': i.height})

        def delete_area():
            for i in range(0, len(areas)):
                for j in range(i + 1, len(areas)):
                    # up
                    if areas[i]['x'] == areas[j]['x'] and areas[i]['width'] == areas[j]['width'] and areas[i]['y'] + areas[i]['height'] + 1 == areas[j]['y']:
                        bpy.ops.screen.area_join(override, 
                                                min_x = areas[i]['x']+1, 
                                                min_y = areas[i]['y'], 
                                                max_x = areas[j]['x']+1,  
                                                max_y = areas[j]['y']+1)
                        areas[i]['height'] = areas[i]['height'] + areas[j]['height'] + 1
                        del areas[j]
                        return
                    # down
                    if areas[i]['x'] == areas[j]['x'] and areas[i]['width'] == areas[j]['width'] and areas[j]['y'] + areas[j]['height'] + 1 == areas[i]['y']:
                        bpy.ops.screen.area_join(override, 
                                                min_x = areas[j]['x']+1, 
                                                min_y = areas[j]['y'], 
                                                max_x = areas[i]['x']+1,  
                                                max_y = areas[i]['y']+1)
                        areas[j]['height'] = areas[j]['height'] + areas[i]['height'] + 1
                        del areas[i]
                        return
                    # right
                    if areas[i]['y'] == areas[j]['y'] and areas[i]['height'] == areas[j]['height'] and areas[i]['x'] + areas[i]['width'] + 1 == areas[j]['x']:
                        bpy.ops.screen.area_join(override, 
                                                min_x = areas[i]['x']+1, 
                                                min_y = areas[i]['y'], 
                                                max_x = areas[j]['x']+1,  
                                                max_y = areas[j]['y']+1)
                        areas[i]['width'] = areas[i]['width'] + areas[j]['width'] + 1
                        del areas[j]
                        return
                    # left
                    if areas[i]['y'] == areas[j]['y'] and areas[i]['height'] == areas[j]['height'] and areas[j]['x'] + areas[j]['width'] + 1 == areas[i]['x']:
                        bpy.ops.screen.area_join(override, 
                                                min_x = areas[j]['x']+1, 
                                                min_y = areas[j]['y'], 
                                                max_x = areas[i]['x']+1,  
                                                max_y = areas[i]['y']+1)
                        areas[j]['width'] = areas[j]['width'] + areas[i]['width'] + 1
                        del areas[i]
                        return

        while len(areas) > 1:
            delete_area()

    def execute(self, context):        # execute() is called by blender when running the operator.
        curr_name = bpy.context.screen.name
        self.delete_areas()

        bpy.data.screens[curr_name + ".001"].name = curr_name
        bpy.data.screens['Robot Compiler'].areas[0].type = 'VIEW_3D'
        #bpy.context.window.screen = bpy.data.screens['Robot Compiler']

        return {'FINISHED'}            # this lets blender know the operator finished successfully.


def register():
    bpy.utils.register_class(RobotCompilerScreen)


def unregister():
    bpy.utils.unregister_class(RobotCompilerScreen)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
