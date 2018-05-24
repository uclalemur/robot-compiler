import bpy
from bpy.types import StringProperty

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