# Python Imports
from enum import Enum

# Blender Imports
import bpy
import bmesh
import mathutils

# Library Imports
from sympy import *


class Material(Enum):
    paper = "paper"
    cardboard = "cardboard"


class Regular_Ngon():
    def __init__(self, name, num_sides, side_length):
        # TODO: validate these variables to be nonneg + normal values
        # TODO: split generation from init
        
        print("Regular_Ngon()")
        
        self.name = name
        self.num_sides = num_sides
        self.side_length = side_length
        self.side_lengths = []
        self.angles = []
        self.material = Material.paper
        
        self.vertices = []
        self.edges = []
        self.faces = []

        self.bmesh = None
        self.mesh = None
        self.object = None
        
        self.generate_geometry()
        self.generate_vertices()
        self.generate_bmesh()
        self.generate_object()
        self.clean_up()
        
    def generate_geometry(self):
        for index in range(0, self.num_sides):
            #name = "side_{0}".format(index)
            symbol = self.side_length
            
            self.side_lengths.append(symbol)
            self.angles.append(2 * pi/self.num_sides)

        self.faces.append(tuple(range(0, self.num_sides)))
            
    def generate_vertices(self):
        self.vertices = [(0,0,0)]
        curr_vertex = (0,0,0)
        angle_from_x = 0
        
        for index in range(0, self.num_sides):
            print(self.side_lengths[index])
            print(self.angles[index])
        
        for index in range(1, self.num_sides):
            x = curr_vertex[0] + cos(angle_from_x) * self.side_lengths[index]
            y = curr_vertex[1] + sin(angle_from_x) * self.side_lengths[index]
            z = curr_vertex[2] + 0
            
            curr_vertex = (x,y,z)
            
            self.vertices.append(curr_vertex)
            
            angle_from_x += self.angles[index]
            
        for vertex in self.vertices:
            print(vertex)

    def generate_bmesh(self):
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
    for index in range(3, 10):
        Regular_Ngon(index, index, 1)
