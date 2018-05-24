#----------------------------------------------------------
# Performs initialization for the electroprogrammatic interface
#----------------------------------------------------------
 
#    Addon info
# bl_info = {
#     'name': 'RoCo Blender Electroprogrammatic',
#     'author': '',
#     'location': 'View3D > UI panel > Add meshes',
#     'category': '3D View'
#     }
 
# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
    import imp
    imp.reload(baseComponents)
    imp.reload(controller)
    imp.reload(panels)
    print("Reloaded multifiles")
else:
    from electroprogrammatic import baseComponents, controller, panels
    print("Imported multifiles")
 
import bpy
from bpy.props import StringProperty

####### Operators ########
class AddNodeOperator(bpy.types.Operator):
    bl_idname = 'object.add_node_operator'
    bl_label = 'Add Input Node'
    nodeType = StringProperty()

    def execute(self, context):
        bpy.ops.node.add_node('INVOKE_DEFAULT', type=self.nodeType)
        # put the node at a an appropriate location
        bpy.ops.node.translate_attach(TRANSFORM_OT_translate={"value": (300, 0, 0)})
        return {'FINISHED'}
 
def register():
    bpy.utils.register_module(__name__)
 
def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register()