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

    def create_object(self):
        print("create_object()")
        self.mesh = bpy.data.meshes.new("{0}_{1}".format(self.name, "mesh"))
        self.object = bpy.data.objects.new(self.name, self.mesh)
        bpy.context.scene.objects.link(self.object)
        
        self.name = self.object.name

        self.polygon_data = self.object.polygon_data

    def wake_object(self):
        print("wake_object()")
        self.mesh = bpy.data.objects[self.name].data
        self.object = bpy.data.objects[self.name]

        self.polygon_data = self.object.polygon_data
        
        self.name = self.polygon_data.name
        self.num_sides = self.polygon_data.num_sides
        
        self.side_names = self.get_vector(self.polygon_data.side_names)
        self.angle_names = self.get_vector(self.polygon_data.angle_names) 
        
        self.side_symbols = self.create_symbols(self.side_names);
        self.angle_symbols = self.create_symbols(self.angle_names);
        
        self.set_constraints(self.get_vector(self.polygon_data.side_constraints),
                            self.get_vector(self.polygon_data.angle_constraints))

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
        # Link bmesh to object mesh
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

        vertex_a = self.object.matrix_world * self.bmesh.verts[self.side_names.index(side_name)].co
        vertex_b = self.object.matrix_world * self.bmesh.verts[(self.side_names.index(side_name) + 1) % len(self.side_names)].co
        
        return vertex_a, vertex_b

    def connect(self, oth, my_side_name, other_side_name, angle):
        # TODO: break out into utils
        print("connect()")
        base = bpy.data.objects[self.name]
        other = bpy.data.objects[oth.name]

        base.select = False
        other.select = False

        base.select = True
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        base.select = False

        other.select = True
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        other.select = False

        v0 = base.matrix_world * base.data.vertices[self.side_names.index(my_side_name)].co
        v1 = base.matrix_world * base.data.vertices[(self.side_names.index(my_side_name) + 1) % len(self.side_names)].co
        v01 = Vector(numpy.subtract(v1,v0))

        o0 = other.matrix_world * other.data.vertices[oth.side_names.index(other_side_name)].co
        o1 = other.matrix_world * other.data.vertices[(oth.side_names.index(other_side_name) + 1) % len(oth.side_names)].co
        o01 = Vector(numpy.subtract(o1, o0))

        # Orient Plane
        base.rotation_mode = 'QUATERNION'
        other.rotation_mode = 'QUATERNION'
        other.rotation_quaternion = base.rotation_quaternion
        
        # Prepare COG
        bpy.context.scene.update()
        o0 = other.matrix_world * other.data.vertices[oth.side_names.index(other_side_name)].co
        o1 = other.matrix_world * other.data.vertices[(oth.side_names.index(other_side_name) + 1) % len(oth.side_names)].co
        bpy.context.scene.cursor_location = (o0 + o1) / 2
        other.select = True
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        other.select = False

        # Location
        other.location = (v0 + v1) / 2

        # Refresh o01 vector
        bpy.context.scene.update()
        o0 = other.matrix_world * other.data.vertices[oth.side_names.index(other_side_name)].co
        o1 = other.matrix_world * other.data.vertices[(oth.side_names.index(other_side_name) + 1) % len(oth.side_names)].co
        o01 = Vector(numpy.subtract(o1, o0))

        # Orient vector
        # Take minimum angle, in case vectors are facing opposite directions
        if o01.rotation_difference(v01).angle < o01.rotation_difference(-v01).angle:
            rot_diff = o01.rotation_difference(v01)
        else:
            rot_diff = o01.rotation_difference(-v01)
        other.rotation_quaternion = rot_diff * other.rotation_quaternion

        # Scaling
        other.scale = Vector((v01.magnitude / o01.magnitude, v01.magnitude / o01.magnitude, v01.magnitude / o01.magnitude))

        # Pivot
        other.rotation_quaternion = mathutils.Matrix.Rotation(math.radians(angle), 4, v01).to_quaternion() * other.rotation_quaternion


if __name__ == '__main__':
    # Regenerate from existing object
    
    """
    poly_a = Polygon("square", [], [])
    poly_a.wake_object()
    if poly_a.solve_geometry():
        if poly_a.generate_vertices():
            poly_a.generate_bmesh()
            poly_a.link_mesh()
            poly_a.clean_up()
    """
    
    poly_a = Polygon("square.001", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_a.create_object()
    poly_a.set_constraints(["1", "2*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_a.solve_geometry():
        if poly_a.generate_vertices():
            poly_a.generate_bmesh()
            poly_a.link_mesh()
            poly_a.clean_up()
            
    poly_b = Polygon("square.002", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_b.create_object()
    poly_b.set_constraints(["1", "3*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_b.solve_geometry():
        if poly_b.generate_vertices():
            poly_b.generate_bmesh()
            poly_b.link_mesh()
            poly_b.clean_up()
    
    poly_c = Polygon("square.003", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_c.create_object()
    poly_c.set_constraints(["1", "1.5 * a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_c.solve_geometry():
        if poly_c.generate_vertices():
            poly_c.generate_bmesh()
            poly_c.link_mesh()
            poly_c.clean_up()
            
    poly_d = Polygon("square.004", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_d.create_object()
    poly_d.set_constraints(["1", "3*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_d.solve_geometry():
        if poly_d.generate_vertices():
            poly_d.generate_bmesh()
            poly_d.link_mesh()
            poly_d.clean_up()
            
    poly_e = Polygon("square.005", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_e.create_object()
    poly_e.set_constraints(["1", "1.5 * a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_e.solve_geometry():
        if poly_e.generate_vertices():
            poly_e.generate_bmesh()
            poly_e.link_mesh()
            poly_e.clean_up()
            
    poly_f = Polygon("square.006", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_f.create_object()
    poly_f.set_constraints(["1", "2*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_f.solve_geometry():
        if poly_f.generate_vertices():
            poly_f.generate_bmesh()
            poly_f.link_mesh()
            poly_f.clean_up()
            
    poly_g = Polygon("square.007", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_g.create_object()
    poly_g.set_constraints(["1", "2*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_g.solve_geometry():
        if poly_g.generate_vertices():
            poly_g.generate_bmesh()
            poly_g.link_mesh()
            poly_g.clean_up()
            
    poly_h = Polygon("square.008", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_h.create_object()
    poly_h.set_constraints(["1", "2*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_h.solve_geometry():
        if poly_h.generate_vertices():
            poly_h.generate_bmesh()
            poly_h.link_mesh()
            poly_h.clean_up()
            
    poly_i = Polygon("square.009", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_i.create_object()
    poly_i.set_constraints(["1", "2*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_i.solve_geometry():
        if poly_i.generate_vertices():
            poly_i.generate_bmesh()
            poly_i.link_mesh()
            poly_i.clean_up()
    
    poly_j = Polygon("trapezoid.001", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_j.create_object()
    poly_j.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_j.solve_geometry():
        if poly_j.generate_vertices():
            poly_j.generate_bmesh()
            poly_j.link_mesh()
            poly_j.clean_up()
            
    poly_k = Polygon("trapezoid.002", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_k.create_object()
    poly_k.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_k.solve_geometry():
        if poly_k.generate_vertices():
            poly_k.generate_bmesh()
            poly_k.link_mesh()
            poly_k.clean_up()
            
    poly_l = Polygon("trapezoid.003", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_l.create_object()
    poly_l.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_l.solve_geometry():
        if poly_l.generate_vertices():
            poly_l.generate_bmesh()
            poly_l.link_mesh()
            poly_l.clean_up()
            
    poly_m = Polygon("trapezoid.004", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_m.create_object()
    poly_m.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_m.solve_geometry():
        if poly_m.generate_vertices():
            poly_m.generate_bmesh()
            poly_m.link_mesh()
            poly_m.clean_up()
            
    poly_n = Polygon("trapezoid.005", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_n.create_object()
    poly_n.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_n.solve_geometry():
        if poly_n.generate_vertices():
            poly_n.generate_bmesh()
            poly_n.link_mesh()
            poly_n.clean_up()
            
    poly_o = Polygon("trapezoid.006", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_o.create_object()
    poly_o.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_o.solve_geometry():
        if poly_o.generate_vertices():
            poly_o.generate_bmesh()
            poly_o.link_mesh()
            poly_o.clean_up()
            
    poly_p = Polygon("trapezoid.007", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_p.create_object()
    poly_p.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_p.solve_geometry():
        if poly_p.generate_vertices():
            poly_p.generate_bmesh()
            poly_p.link_mesh()
            poly_p.clean_up()
            
    poly_q = Polygon("trapezoid.008", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_q.create_object()
    poly_q.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_q.solve_geometry():
        if poly_q.generate_vertices():
            poly_q.generate_bmesh()
            poly_q.link_mesh()
            poly_q.clean_up()
 
    poly_a.connect(poly_b, poly_a.side_names[0], poly_b.side_names[0], 90)
    poly_a.connect(poly_c, poly_a.side_names[1], poly_c.side_names[0], -90)
    poly_a.connect(poly_d, poly_a.side_names[2], poly_d.side_names[0], -90)
    poly_a.connect(poly_e, poly_a.side_names[3], poly_e.side_names[0], -90)
    
    poly_b.connect(poly_f, poly_c.side_names[2], poly_f.side_names[0], -80)
    poly_d.connect(poly_g, poly_d.side_names[2], poly_g.side_names[0], 80)
    
    poly_f.connect(poly_h, poly_f.side_names[2], poly_h.side_names[0], 20)
    poly_g.connect(poly_i, poly_g.side_names[2], poly_i.side_names[0], -20)
    
    poly_f.connect(poly_j, poly_f.side_names[1], poly_j.side_names[1], -60)
    poly_f.connect(poly_k, poly_f.side_names[3], poly_k.side_names[1], 120)
    
    poly_g.connect(poly_l, poly_g.side_names[1], poly_l.side_names[1], 60)
    poly_g.connect(poly_m, poly_g.side_names[3], poly_m.side_names[1], -120)
    
    poly_h.connect(poly_n, poly_h.side_names[1], poly_n.side_names[1], -60)
    poly_h.connect(poly_o, poly_h.side_names[3], poly_o.side_names[1], 120)
    
    poly_i.connect(poly_p, poly_i.side_names[1], poly_p.side_names[1], 60)
    poly_i.connect(poly_q, poly_i.side_names[3], poly_q.side_names[1], -120)
    
if __name__ == '__main__2':
    # Regenerate from existing object
    
    """
    poly_a = Polygon("square", [], [])
    poly_a.wake_object()
    if poly_a.solve_geometry():
        if poly_a.generate_vertices():
            poly_a.generate_bmesh()
            poly_a.link_mesh()
            poly_a.clean_up()
    """
    
    poly_a = Polygon("square", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_a.create_object()
    poly_a.set_constraints(["3", "a", "a", "a"], ["pi/2", "ab", "ab", "ab"])
    if poly_a.solve_geometry():
        if poly_a.generate_vertices():
            poly_a.generate_bmesh()
            poly_a.link_mesh()
            poly_a.clean_up()
            
    poly_b = Polygon("square.001", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_b.create_object()
    poly_b.set_constraints(["2", "a", "a", "a"], ["pi/2", "ab", "ab", "ab"])
    if poly_b.solve_geometry():
        if poly_b.generate_vertices():
            poly_b.generate_bmesh()
            poly_b.link_mesh()
            poly_b.clean_up()
       
    poly_c = Polygon("triangle_345", ["a", "b", "c"], ["ab", "bc", "ca"])
    poly_c.create_object()
    poly_c.set_constraints(["3", "4", "5"], ["pi/2", "atan(a/b)", "pi-ab-bc"])
    if poly_c.solve_geometry():
        if poly_c.generate_vertices():
            poly_c.generate_bmesh()
            poly_c.link_mesh()
            poly_c.clean_up()
    
    poly_d = Polygon("triangle_aab", ["a", "b", "c"], ["ab", "bc", "ca"])
    poly_d.create_object()
    poly_d.set_constraints(["5", "a", "(a**2+b**2)**(1/2)"], ["pi/2", "atan(a/b)", "pi-ab-bc"])
    if poly_d.solve_geometry():
        if poly_d.generate_vertices():
            poly_d.generate_bmesh()
            poly_d.link_mesh()
            poly_d.clean_up()
            
    poly_e = Polygon("rhombus", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_e.create_object()
    poly_e.set_constraints(["1", "a", "a", "b"], ["pi/3", "pi-ab", "ab", "bc"])
    if poly_e.solve_geometry():
        if poly_e.generate_vertices():
            poly_e.generate_bmesh()
            poly_e.link_mesh()
            poly_e.clean_up()
    
    poly_f = Polygon("trapezoid", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_f.create_object()
    poly_f.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_f.solve_geometry():
        if poly_f.generate_vertices():
            poly_f.generate_bmesh()
            poly_f.link_mesh()
            poly_f.clean_up()
    
    poly_g = Polygon("trapezoid", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_g.create_object()
    poly_g.set_constraints(["2.5", "2*a", "a", "b-2*a*sin(cd-pi/2)"], ["pi/3", "ab", "pi-ab", "cd"])
    if poly_g.solve_geometry():
        if poly_g.generate_vertices():
            poly_g.generate_bmesh()
            poly_g.link_mesh()
            poly_g.clean_up()
    
    poly_h = Polygon("quad_long", ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
    poly_h.create_object()
    poly_h.set_constraints(["1.5", "2*a", "a", "b"], ["pi/2", "ab", "ab", "ab"])
    if poly_h.solve_geometry():
        if poly_h.generate_vertices():
            poly_h.generate_bmesh()
            poly_h.link_mesh()
            poly_h.clean_up()
    
    poly_a.connect(poly_b, poly_a.side_names[0], poly_b.side_names[0], 120)
    poly_b.connect(poly_f, poly_b.side_names[2], poly_f.side_names[0], 100)
    poly_f.connect(poly_g, poly_f.side_names[3], poly_g.side_names[3], 120)
    poly_g.connect(poly_c, poly_g.side_names[1], poly_c.side_names[0], 90)
    poly_c.connect(poly_d, poly_c.side_names[2], poly_d.side_names[2], 121)
    poly_a.connect(poly_e, poly_a.side_names[1], poly_e.side_names[0], 80)
    poly_a.connect(poly_h, poly_a.side_names[2], poly_h.side_names[3], -50)

    #nonlinsolve([parse_expr("a-b"), parse_expr("c-(a**2+b**2)**(1/2)"), parse_expr("c-1")], [a, b, c])
