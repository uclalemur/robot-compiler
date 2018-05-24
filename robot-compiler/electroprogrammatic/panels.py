import bpy

####### Panels ########
class ToolsPanel(bpy.types.Panel):
    ''' creates panel that shows up on the tool bar left
    of the node editor
    '''
    bl_label = "Subcomponents"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"

    def draw(self, context):
        # add buttons for all nodes set the nodeType property in the add node operator
        self.layout.operator('object.add_node_operator', text='Timer Node').nodeType = 'TimerNodeType'
        self.layout.operator('object.add_node_operator', text='Blink LED Node').nodeType = 'BlinkLEDNodeType'
        self.layout.operator('object.add_node_operator', text='Logical Node').nodeType = 'LogicalNodeType'
        self.layout.operator('object.add_node_operator', text='Serial In Node').nodeType = 'SerialInNodeType'
        self.layout.operator('object.add_node_operator', text='Button Node').nodeType = 'ButtonNodeType'
        self.layout.operator('object.add_node_operator', text='If Node').nodeType = 'IfNodeType'
        self.layout.operator('object.add_node_operator', text='Motor Node').nodeType = 'MotorNodeType'
