from stl import mesh
from stl import stl
import math
import numpy
from matplotlib import pyplot
from mpl_toolkits import mplot3d
import os
import pprint as pp
import sys
if len(sys.argv) == 2:
	print("with sympy")
	import sympy
else:
	print("without sympy")
	import math as sympy
from functions import * 

attach = []
attach_compressor = []
propeller = []
sections = []


#alle mål er i micrometer ( 1/1000 millimeter )
scale = 1



#specs
cylinder_radius = 5*scale
cylinder_height = 10*scale
cylinder_offset = 0

blades = 1
blade_radius = 38*scale
blade_thickness = 1*scale
# blade_angles = [20,  45]
blade_angles = [sympy.pi/4,  sympy.pi/2.7]
blade_mount_depth = 3*scale
blade_mount_curve_resolution = 9*scale

duct_ratio = 2
duct_gap = 1/10*scale
duct_thickness = 1*scale
duct_height = duct_ratio*cylinder_height
duct_offset = 0


def clss():
    os.system('cls' if os.name=='nt' else 'clear')
clss()



inner_prop = make_propeller_v2(cylinder_radius, blade_radius - blade_mount_depth, blade_thickness, 1, blade_angles[0], blade_angles[1])
# mount = make_propeller_mount(cylinder_height, blade_thickness, blade_mount_depth )
# mount = move_vector(mount, numpy.array([cylinder_radius - blade_mount_depth, 0, 0]))
# combined = numpy.append(inner_prop, mount)

combined = mesh.Mesh(inner_prop)

combined.save(filename="test.stl")

os.system('{}\\test.stl'.format(os.getcwd()))