import os
import sys
import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import IntProperty, FloatProperty, EnumProperty, StringProperty, BoolProperty,PointerProperty

file_path = os.path.abspath(os.path.dirname(__file__))
# append current working dir to python path
sys.path.append(file_path)
#from operators import AddInputNodeOperator, AddTimerNodeOperator

# Implementation of custom nodes from Python

TYPES = ['INT', 'BOOLEAN', 'STRING']
INT_SOCKET_COLOR = (0.4, 0.216, 1.0, 0.5)
STRING_SOCKET_COLOR = (0.6, 0.4, 0.216, 0.5)
BOOL_SOCKET_COLOR = (0.5, 0.4, 0.5, 0.5)
UNSPECIFIED_SOCKET_COLOR = (1.0, 1.0, 1.0, 0.5)

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class CustomTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'CustomTreeType'

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class CustomTree(NodeTree):
    # Description string
    '''A custom node tree type that will show up in the node editor header'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'CustomTreeType'
    # Label for nice name display
    bl_label = 'Custom Node Tree'
    # Icon identifier
    bl_icon = 'NODETREE'


    
class BaseNode(Node, CustomTreeNode):
    '''
    defines methods inherited by all nodes:
        - update
        - copy
        - remove
    '''
    bl_idname = 'BaseNodeType'
    bl_label = 'Base Node'
    
    def update(self):
        print('update node ', self)
        
    def socket_value_update(self, context):
        print('socket value udpate ', self)

    def copy(self, node):
        pass

    def free(self):
        pass

# class Spec(PropertyGroup):
#     name = StringProperty() #Parent node name 

#     def setVal(self, name, call):
#         self.name = name


# checks the output from the from_socket
class CustomNodeSocket(NodeSocket):
    bl_idname = 'CustomNodeSocketType'
    # Label for nice name display
    bl_label = 'Custom Node Socket'

    # limit # of links to 1
    def init(self, context):
        self.link_limit = 1

    def draw(self, context, layout, node, text):
        if not self.is_output and self.is_linked:
            # if input socket type
            # see what the input socket is connected with an update type
            node_link = self.links[0]
            from_socket_type = node_link.from_socket.type
            layout.label(from_socket_type)

    def draw_color(self, context, node):
        if not self.is_linked:
            return UNSPECIFIED_SOCKET_COLOR 
        else:
            node_link = self.links[0]
            node_type = node_link.to_socket.type if self.is_output else node_link.from_socket.type
            if node_type == 'STRING':
                return STRING_SOCKET_COLOR
            elif node_type == 'INT':
                return INT_SOCKET_COLOR
            elif node_type == 'BOOLEAN':
                return BOOL_SOCKET_COLOR
        

class TimerNode(BaseNode):
    ''' timer class accepts a callback and execute a function after n seconds '''
    bl_idname = 'TimerNodeType'
    bl_label = 'Time Node'
    # interval 
    # initial timeout
    arg1 = FloatProperty(default=0)
    # interval
    arg2 = FloatProperty(default=5)
    #spec = PointerProperty(type=Spec).setVal(self.name)
    

    def init(self, context):
        self.outputs.new('NodeSocketBool', 'TimerOutput')

    def draw_buttons(self, context, layout):
        layout.label('Initial Timeout')
        layout.prop(self, 'arg1')
        layout.label('Interval')
        layout.prop(self, 'arg2')

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'arg1')
        layout.prop(self, 'arg2')

    def draw_label(self):
        return 'Timer Node'

def nodeUpdate(self, context):
    self.inputs.clear()

    if self.arg4 == BlinkLEDNode.INPUTCONDITION:
        self.inputs.new('NodeSocketBool', 'analog in')

class BlinkLEDNode(BaseNode):
    ''' timer class accepts a callback and execute a function after n seconds '''
    SETINTERVAL = 'SETINT ERVAL'
    INPUTCONDITION = 'INPUTCONDITION'

    bl_idname = 'BlinkLEDNodeType'
    bl_label = 'Blink LED Node'
    
    # brightness
    arg1 = FloatProperty(default=512)
    # initial timeout
    arg2 = FloatProperty(default=0)
    # interval
    arg3 = FloatProperty(default=5)

    options = [
        (SETINTERVAL, 'Set Interval', 'blink led with setInterval'),
        (INPUTCONDITION, 'Condition on Input Port', 'blink led based on input port')
    ]

    # logic
    arg4 = EnumProperty(name="Blink Mode", description="how to blink the led", 
        items=options, default=SETINTERVAL, update=nodeUpdate)

    def draw_buttons(self, context, layout):
        if self.arg4 == self.SETINTERVAL:
            layout.label('Brightness')
            layout.prop(self, 'arg1')
            layout.label('Initial Timeout')
            layout.prop(self, 'arg2')
            layout.label('Interval')
            layout.prop(self, 'arg3')
        layout.prop(self, 'arg4')


    def draw_buttons_ext(self, context, layout):
        layout.label('Brightness')
        layout.prop(self, 'arg1')
        layout.label('Initial Timeout')
        layout.prop(self, 'arg2')
        layout.label('Interval')
        layout.prop(self, 'arg3') 
        layout.label('Logic')
        layout.prop(self, 'arg4')     

    def draw_label(self):
        return 'Blink LED Node'

class LogicalNode(BaseNode):
    AND = 'AND'
    OR = 'OR'
    XOR = 'XOR'
    NOR = 'NOR'

    bl_idname = 'LogicalNodeType'
    bl_label = 'Logical Node'

    # logic options: AND, OR, XOR, NOR
    options = [
        ('AND', 'And', 'Logical And'),
        ('OR', 'OR', 'Logical OR'),
        ('XOR', 'XOR', 'Logical XOR'),
        ('NOR', 'NOR', 'Logical NOR')
    ]

    # logic
    arg1 = EnumProperty(name='Logical Options', description='logical options',
        items=options, default=AND)
        

    def init(self, context):
        self.inputs.new('NodeSocketBool', 'input1')
        self.inputs.new('NodeSocketBool', 'input2')
        self.outputs.new('NodeSocketBool', 'result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'arg1')

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'arg1')

    def draw_label(self):
        return 'Logical Node'

class SerialInNode(BaseNode):
    bl_idname = 'SerialInNodeType'
    bl_label = 'Serial In Node'

    # pin name
    arg1 = StringProperty(name='pin', description='pin to read serial from ')
    
    def init(self, context):
        self.outputs.new('CustomNodeSocketType', 'serialInput')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'arg1')

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'arg1')

    def draw_label(self):
        return 'Serial Input Node'

class ButtonNode(BaseNode):
    bl_idname = 'ButtonNodeType'
    bl_label = 'Button Node'

    # pin name
    arg1 = StringProperty(name='pin', description='pin to read button status ')

    def init(self, context):
        self.outputs.new('NodeSocketBool', 'buttonPressed')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'arg1')

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'arg1')

    def draw_label(self):
        return 'Button Node'

class IfNode(BaseNode):
    bl_idname = 'IfNodeType'
    bl_label = 'If Node'

    typesOfComparison = [
        ('EQ', 'Equal', 'Comparison Equal'),
        ('NEQ', 'Not Equal', 'Comparison Not Equal'),
        ('LT', 'Less Than', 'Comparison Less than'),
        ('GT', 'Greater Than', 'Comparison Greater than'),
        ('LTEQ', 'Less than or equal to', 'Comparison Less than equal to'),
        ('GTEQ', 'Greater than or equal to ', 'Comparison greater than equal to'),
    ]

    # type of comparison
    arg1 = EnumProperty(name='comparisonType', description='type of comparison',
        items=typesOfComparison)
    
    def init(self, context):
        self.inputs.new('CustomNodeSocketType', 'compareThing')
        self.inputs.new('CustomNodeSocketType', 'compareTo')
        self.outputs.new('NodeSocketBool', 'result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'arg1')

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'arg1')

    def draw_label(self):
        return self.bl_label

class MotorNode(BaseNode):
    ''' timer class accepts a callback and execute a function after n seconds '''
    SETINTERVAL = 'SETINT ERVAL'
    INPUTCONDITION = 'INPUTCONDITION'

    bl_idname = 'MotorNodeType'
    bl_label = 'Motor Node'
    # speed 
    arg1 = FloatProperty(default=50)

    def init(self, context):
        self.inputs.new("NodeSocketBool", "driver port")
        #self.inputs.new("CustomInputSocketType", "test port")

    def draw_buttons(self, context, layout):
        layout.label('Motor Speed')
        layout.prop(self, 'arg1')

    def draw_buttons_ext(self, context, layout):
        layout.label('Motor Speed')
        layout.prop(self, 'arg1')     

    def draw_label(self):
        return 'Drive a motor'

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)



if __name__ == "__main__":
    s = 1
    if s == 0:
        unregister()
    else:
        register()
        
