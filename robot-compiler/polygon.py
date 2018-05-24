# TODO: Minimize imports
# Python Imports
from enum import Enum

# Blender Imports
import bpy
import bmesh
import mathutils
from mathutils import Vector

# Library Imports
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import math
import numpy

class Material(Enum):
    paper = "paper"
    cardboard = "cardboard"


# TODO: pass pylint
class Polygon():
    def __init__(self, name, side_names, angle_names): 
        # TODO: validate these variables to be nonneg + normal values
        # TODO: split generation from init
        
        print("Polygon.__init__()")

        # Immutable specifications
        self.name = name
        self.num_sides = len(side_names)

        #
        self.side_names = side_names
        self.angle_names = angle_names

        # 
        self.side_symbols = self.create_symbols(side_names);
        self.angle_symbols = self.create_symbols(angle_names);

        #
        self.side_constraints = []
        self.angle_constraints = []

        self.parsed_side_constraints = []
        self.parsed_angle_constraints = []

        # Mutable specifications
        self.sides = []
        self.angles = []
        #self.material = Material.paper

        # Geometry
        self.vertices = []
        self.edges = []
        self.faces = []

        # Actual mesh
        self.bmesh = None
        self.mesh = None
        self.object = None

        # Persistent data
        self.polygon_data = None

        # Get existing object, if possible, otherwise create one and link to scene
        self.get_object()

        # Get existing polygon_data, if possible
        self.get_polygon_data()


    def get_object(self):
        if self.name in bpy.data.objects.keys():
            print("get_object 1")
            self.mesh = bpy.data.objects[self.name].data
            self.object = bpy.data.objects[self.name]
            return

        print("get_object 2")
        self.mesh = bpy.data.meshes.new("{0}_{1}".format(self.name, "mesh"))
        self.object = bpy.data.objects.new(self.name, self.mesh)
        bpy.context.scene.objects.link(self.object)

    def get_polygon_data(self):
        if self.object.polygon_data.name == self.name:
            print("get_polygon_data 1")
           
            self.polygon_data = self.object.polygon_data
            
            self.name = self.polygon_data.name
            self.num_sides = self.polygon_data.num_sides
            
            self.side_names = self.get_vector(self.polygon_data.side_names)
            self.angle_names = self.get_vector(self.polygon_data.angle_names) 
            
            self.side_symbols = self.create_symbols(self.side_names);
            self.angle_symbols = self.create_symbols(self.angle_names);
            
            self.set_constraints(self.get_vector(self.polygon_data.side_constraints),
                                self.get_vector(self.polygon_data.angle_constraints))
            
            return
        
        print("get_polygon_data 2")
        self.polygon_data = self.object.polygon_data

    def set_vector(self, collection, values):
        collection.clear()
        for index, value in enumerate(values):
            collection.add()
            collection[index].value = value
        
    def get_vector(self, collection):
        return [element.value for element in collection]
        
    def create_symbols(self, names):
        print("Polygon.create_symbols()")
        return [Symbol(name) for name in names]
    
    def set_constraints(self, side_constraints, angle_constraints):
        print("Polygon.set_constraints()")
        # TODO: check len(sides) == len(side_names)
        # TODO: repeat on angles
        # TODO: split this stuff into a reset
        self.side_constraints = []
        self.angle_constraints = []
        self.parsed_side_constraints = []
        self.parsed_angle_constraints = []

        # Side
        for index, side_constraint in enumerate(side_constraints):
            full_constraint = "{0}{1}{2}{3}".format(self.side_symbols[index], "- (", side_constraint, ")")
            self.side_constraints.append(side_constraint)
            self.parsed_side_constraints.append(parse_expr(full_constraint))
            
        # Angle
        for index, angle_constraint in enumerate(angle_constraints):
            full_constraint = "{0}{1}{2}{3}".format(self.angle_symbols[index], "- (", angle_constraint, ")")
            self.angle_constraints.append(angle_constraint)
            self.parsed_angle_constraints.append(parse_expr(full_constraint))

        # Extra that are necessary
        full_constraint = "{0}{1}{2}".format(self.num_sides - 2, " * pi - ", "-".join(self.angle_names))
        self.parsed_angle_constraints.append(parse_expr(full_constraint))

        self.faces.append(tuple(range(0, self.num_sides)))
    
    
    def solve_geometry(self):
        print("Polygon.solve_geometry()")

        # Combined solve bc angles may rely on sides and vv        
        sol = solve(self.parsed_side_constraints + self.parsed_angle_constraints, self.side_symbols + self.angle_symbols, dict=True)
        if len(sol) == 0:
            print("Constraints not solvable")
            return False
        sol = sol[0]

        for symbol in self.side_symbols:
            self.sides.append(sol[symbol])
            
        for symbol in self.angle_symbols:
            self.angles.append(sol[symbol])

        return True
    
    def generate_vertices(self):
        print("Polygon.generate_vertices()")

        curr_vertex = (0,0,0)
        self.vertices = [curr_vertex]
        angle_from_x = 0
        
        for index in range(0, self.num_sides - 1):
            x = curr_vertex[0] + cos(angle_from_x) * self.sides[index]
            y = curr_vertex[1] + sin(angle_from_x) * self.sides[index]
            z = curr_vertex[2] + 0
            
            curr_vertex = (x,y,z)
            
            self.vertices.append(curr_vertex)
            
            angle_from_x += pi - self.angles[index]

        x = curr_vertex[0] + cos(angle_from_x) * self.sides[self.num_sides - 1]
        y = curr_vertex[1] + sin(angle_from_x) * self.sides[self.num_sides - 1]
        z = curr_vertex[2] + 0
        
        if not math.isclose(x, self.vertices[0][0], abs_tol=1e-10) or not math.isclose(y, self.vertices[0][1], abs_tol=1e-10) or not math.isclose(z, self.vertices[0][2], abs_tol=1e-10):
            print("Constraints not solvable")
            return False

        #for vertex in self.vertices:
        #    print(vertex)

        return True

    def generate_bmesh(self):
        print("Polygon.generate_bmesh()")

        if len(self.vertices) <= 2:
            print("Must have at least three self.vertices")
            return

        self.bmesh = bmesh.new()
        [self.bmesh.verts.new(co) for co in self.vertices]
        self.bmesh.verts.index_update()
        self.bmesh.verts.ensure_lookup_table()

        if self.faces:
            for face in self.faces:
                self.bmesh.faces.new(tuple(self.bmesh.verts[i] for i in face))
            self.bmesh.faces.index_update()

        if self.edges:
            for edge in self.edges:
                edge_seq = tuple(self.bmesh.verts[i] for i in edge)
                try:
                    self.bmesh.edges.new(edge_seq)
                except ValueError:
                    # edge exists!
                    pass

            self.bmesh.edges.index_update()

    def link_mesh(self):
        #
        self.bmesh.to_mesh(self.mesh)

    def clean_up(self):
        # Deselect all
        #bpy.context.scene.objects.active = other.object
        bpy.ops.object.select_all(action='DESELECT')
        
        
        # Use this for persisting data at the end
        # TODO: deal with duplicate names, Ex: poly.001
        self.polygon_data.name = self.name
        self.polygon_data.num_sides = self.num_sides
        
        self.set_vector(self.polygon_data.side_names, self.side_names)
        self.set_vector(self.polygon_data.angle_names, self.angle_names)
        self.set_vector(self.polygon_data.side_constraints, self.side_constraints)        
        self.set_vector(self.polygon_data.angle_constraints, self.angle_constraints)
        
    
    def side_name_to_vertices(self, side_name):
        # TODO: index checking
        vertex_a = self.vertices[self.side_names.index(side_name)]
        vertex_b = self.vertices[(self.side_names.index(side_name) + 1) % len(self.side_names)]
        
        return vertex_a, vertex_b

    def connect(self, other, my_side_name, other_side_name, angle):
        # Move center of other.other_side_name to center of self.my_side_name
        # TODO: Break out into a utils method
        # TODO: Make it work for different orientations
        # TODO: Decide on whether we want scaling or to propagate it

        other.object.select = True
        
        poly_v0, poly_v1 = self.side_name_to_vertices(my_side_name)
        other_v0, other_v1 = other.side_name_to_vertices(other_side_name)

        bpy.context.scene.cursor_location = ((other_v0[0] + other_v1[0]) /2, (other_v0[1] + other_v1[1]) / 2, (other_v0[2] + other_v1[2]) / 2)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        poly_vector = Vector(tuple(numpy.subtract(poly_v0, poly_v1)))
        other_vector = Vector(tuple(numpy.subtract(other_v1, other_v0)))
        
        other.object.rotation_euler[2] = poly_vector.xy.angle_signed(other_vector.xy, 0.0)

        other.object.location[0] = (poly_v0[0] + poly_v1[0]) / 2
        other.object.location[1] = (poly_v0[1] + poly_v1[1]) / 2
        other.object.location[2] = (poly_v0[2] + poly_v1[2]) / 2

        other.object.scale[0] = poly_vector.magnitude / other_vector.magnitude
        other.object.scale[1] = poly_vector.magnitude / other_vector.magnitude
        other.object.scale[2] = poly_vector.magnitude / other_vector.magnitude
        
        other.object.rotation_euler[0] = math.radians(angle)
        
        self.clean_up()


if __name__ == '__main__':
    """
    # Regenerate from existing object
    poly = Polygon("poly7", [], [])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.link_mesh()
            poly.clean_up()
    """
    
    poly_a = Polygon("square1", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_a.set_constraints(["2", "a", "a", "a"], ["pi/2", "ab", "ab", "ab"])
    if poly_a.solve_geometry():
        if poly_a.generate_vertices():
            poly_a.generate_bmesh()
            poly_a.link_mesh()
            poly_a.clean_up()
    
    poly_b = Polygon("square2", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_b.set_constraints(["1", "a", "a", "a"], ["pi/2", "ab", "ab", "ab"])
    if poly_b.solve_geometry():
        if poly_b.generate_vertices():
            poly_b.generate_bmesh()
            poly_b.link_mesh()
            poly_b.clean_up()
            
    poly_c = Polygon("quad_trap", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_c.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_c.solve_geometry():
        if poly_c.generate_vertices():
            poly_c.generate_bmesh()
            poly_c.link_mesh()
            poly_c.clean_up()
            
    poly_d = Polygon("triangle_345", ["a", "b", "c"], ["ab", "bc", "ca"])
    poly_d.set_constraints(["3", "4", "5"], ["pi/2", "atan(a/b)", "pi-ab-bc"])
    if poly_d.solve_geometry():
        if poly_d.generate_vertices():
            poly_d.generate_bmesh()
            poly_d.link_mesh()
            poly_d.clean_up()
            
    poly_e = Polygon("quad_rhombus", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_e.set_constraints(["1", "a", "a", "b"], ["pi/3", "pi-ab", "ab", "bc"])
    if poly_e.solve_geometry():
        if poly_e.generate_vertices():
            poly_e.generate_bmesh()
            poly_e.link_mesh()
            poly_e.clean_up()        
    
    poly_c.connect(poly_b, poly_c.side_names[0], poly_b.side_names[0], -20)
    poly_c.connect(poly_a, poly_c.side_names[1], poly_a.side_names[0], 30)
    poly_c.connect(poly_d, poly_c.side_names[2], poly_d.side_names[0], 40)
    poly_c.connect(poly_e, poly_c.side_names[3], poly_e.side_names[0], 60)

    """

    poly = Polygon("triangle_345", ["a", "b", "c"], ["ab", "bc", "ca"])
    poly.set_constraints(["3", "4", "5"], ["pi/2", "atan(a/b)", "pi-ab-bc"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.link_mesh()
            poly.clean_up()
            
    poly = Polygon("triangle_aab", ["a", "b", "c"], ["ab", "bc", "ca"])
    poly.set_constraints(["5", "a", "(a**2+b**2)**(1/2)"], ["pi/2", "atan(a/b)", "pi-ab-bc"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.link_mesh()
            poly.clean_up()
            
    poly = Polygon("quad_square", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly.set_constraints(["1", "a", "a", "a"], ["pi/2", "ab", "ab", "ab"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.link_mesh()
            poly.clean_up()
            
    poly = Polygon("quad_long", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly.set_constraints(["1.5", "2*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.link_mesh()
            poly.clean_up()
            
    poly = Polygon("quad_rhombus", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly.set_constraints(["2", "2*a", "a", "b"], ["pi/3", "pi-ab", "ab", "bc"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.link_mesh()
            poly.clean_up()
            
    poly = Polygon("quad_trap", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.link_mesh()
            poly.clean_up()

    #nonlinsolve([parse_expr("a-b"), parse_expr("c-(a**2+b**2)**(1/2)"), parse_expr("c-1")], [a, b, c])
    """
