import bpy
from roco import polygon

bl_info = {
    "name": "Robot Compiler",
    "description": "Robotics codesign and fabrication tool",
    "author": "UCLA LEMUR",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "",
    "warning": "", 
    "wiki_url": "",
    "tracker_url": "",
    "support": "TESTING",
    "category": "Object",
}


# TODO: pass pylint
class RobotCompiler(bpy.types.Operator):
    bl_idname = "robot_compiler.screen"        # unique identifier for buttons and menu items to reference.
    bl_label = "Robot Compiler"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}


# Blender does not have a bpy.props.StringVectorProperty
# and we cannot create a CollectionProperty of type bpy.props.StringProperty
# so we create a wrapper
class CustomStringProperty(bpy.types.PropertyGroup):
    value = bpy.props.StringProperty()


# 
class PolygonData(bpy.types.PropertyGroup):
    # Immutable specifications
    name = bpy.props.StringProperty()
    num_sides = bpy.props.IntProperty()

    #
    side_names = bpy.props.CollectionProperty(type=CustomStringProperty)
    angle_names = bpy.props.CollectionProperty(type=CustomStringProperty)
    

    #
    side_constraints = bpy.props.CollectionProperty(type=CustomStringProperty)
    angle_constraints = bpy.props.CollectionProperty(type=CustomStringProperty)
    
    # Mutable specifications, not sure if this shoudl be in persistent data or not
    #sides = bpy.props.FloatVectorProperty()
    #angles = bpy.props.FloatVectorProperty()
    
    #self.material = Material.paper


def register():
    bpy.utils.register_class(RobotCompiler)
    bpy.utils.register_class(CustomStringProperty)
    bpy.utils.register_class(PolygonData)
    bpy.types.Object.polygon_data = bpy.props.PointerProperty(type=PolygonData)


def unregister():
    bpy.utils.unregister_class(RobotCompiler)
    bpy.utils.unregister_class(CustomStringProperty)
    bpy.utils.unregister_class(PolygonData)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
