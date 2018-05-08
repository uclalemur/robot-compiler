# Python Imports
from enum import Enum

# Blender Imports
import bpy
import bmesh
#import mathutils

# Library Imports
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from math import *

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

    def create_symbols(self, names):
        print("Polygon.create_symbols()")
        return [Symbol(name) for name in names]

    def set_constraints(self, sides, angles):
        print("Polygon.set_constraints()")
        # TODO: check len(sides) == len(side_names)
        # TODO: repeat on angles
        # TODO: split this stuff into a reset
        self.sides = []
        self.angles = []
        self.side_constraints = []
        self.angle_constraints = []

        # Side
        for index, side in enumerate(sides):
            constraint = "{0}{1}{2}{3}".format(self.side_symbols[index], "- (", side, ")")
            self.side_constraints.append(parse_expr(constraint))
            
        # Angle
        for index, angle in enumerate(angles):
            constraint = "{0}{1}{2}{3}".format(self.angle_symbols[index], "- (", angle, ")")
            self.angle_constraints.append(parse_expr(constraint))

        # Extra that are necessary
        constraint = "{0}{1}{2}".format(self.num_sides - 2, " * pi - ", "-".join(self.angle_names))
        self.angle_constraints.append(parse_expr(constraint))

        print(self.side_constraints)
        print(self.angle_constraints)

        self.faces.append(tuple(range(0, self.num_sides)))
        
    def solve_geometry(self):
        print("Polygon.solve_geometry()")

        print(self.side_constraints + self.angle_constraints)
        print(self.side_symbols + self.angle_symbols)

        # Combined solve bc angles may rely on sides and vv        
        sol = solve(self.side_constraints + self.angle_constraints, self.side_symbols + self.angle_symbols, dict=True)
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

        self.vertices = [(0,0,0)]
        curr_vertex = (0,0,0)
        angle_from_x = 0
        
        print(self.sides)
        print(self.angles)
        
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

        print(self.vertices[0][0])
        print(self.vertices[0][1])
        print(self.vertices[0][2])
        
        print(x)
        print(y)
        print(z)
        
        if not isclose(x, self.vertices[0][0], abs_tol=1e-10) or not isclose(y, self.vertices[0][1], abs_tol=1e-10) or not isclose(z, self.vertices[0][2], abs_tol=1e-10):
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
    
    def generate_object(self):
        # Create Object and link to scene
        self.mesh = bpy.data.meshes.new("{0}_{1}".format(self.name, "mesh"))
        self.object = bpy.data.objects.new("{0}_{1}".format(self.name, "object"), self.mesh)
        bpy.context.scene.objects.link(self.object)
        self.bmesh.to_mesh(self.mesh)

    def clean_up(self):
        # Select the object
        bpy.context.scene.objects.active = self.object
        self.object.select = True


if __name__ == '__main__':
    poly = Polygon("triangle_345", ["a", "b", "c"], ["ab", "bc", "ca"])
    poly.set_constraints(["3", "4", "5"], ["pi/2", "atan(a/b)", "pi-ab-bc"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.generate_object()
            poly.clean_up()
            
    poly = Polygon("triangle_aab", ["a", "b", "c"], ["ab", "bc", "ca"])
    poly.set_constraints(["5", "a", "(a**2+b**2)**(1/2)"], ["pi/2", "atan(a/b)", "pi-ab-bc"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.generate_object()
            poly.clean_up()
            
    poly = Polygon("quad_square", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly.set_constraints(["1", "a", "a", "a"], ["pi/2", "ab", "ab", "ab"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.generate_object()
            poly.clean_up()
            
    poly = Polygon("quad_long", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly.set_constraints(["1.5", "2*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.generate_object()
            poly.clean_up()
            
    poly = Polygon("quad_rhombus", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly.set_constraints(["2", "2*a", "a", "b"], ["pi/3", "pi-ab", "ab", "bc"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.generate_object()
            poly.clean_up()
            
    poly = Polygon("quad_trap", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly.solve_geometry():
        if poly.generate_vertices():
            poly.generate_bmesh()
            poly.generate_object()
            poly.clean_up()


    #nonlinsolve([parse_expr("a-b"), parse_expr("c-(a**2+b**2)**(1/2)"), parse_expr("c-1")], [a, b, c])
            
