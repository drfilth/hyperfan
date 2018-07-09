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
scale = 2


#compressor sections
section_height = 6*scale
section_height_2 = section_height
section_offset = 0*scale
section_radius = 10*scale
section_blade_radius_increment_ratio = 0.5
sections_amount = 6
section_blade_density = 2.5*scale # 3*scale 
section_blade_thickness = [0.5*scale, 0.25*scale]
section_prop_radius_outer = section_radius + 1*scale

section_blade_angles = [sympy.pi/4,  sympy.pi/4]
section_stator_angles = [sympy.pi/4 + sympy.pi/2,  sympy.pi/4 + sympy.pi/2]

#other
compressor_height = sections_amount * section_height
compressor_radius = section_prop_radius_outer + 1
compressor_thickness = 1*scale
compressor_offset = 0*scale

rod1_radius = 2.2*scale
rod1_height = 1*scale
rod1_offset = compressor_height + compressor_offset

cylinder_radius = 5*scale
cylinder_height = 10*scale
cylinder_offset = rod1_offset + rod1_height

blades = 8
blade_radius = 50*scale
blade_thickness = [1*scale, 1*scale]
# blade_angles = [20,  45]
blade_angles = [sympy.pi/9,  sympy.pi/4]

duct_ratio = 2
duct_gap = 1/10*scale
duct_thickness = 1*scale
duct_height = duct_ratio*cylinder_height
duct_offset = cylinder_offset - cylinder_offset/duct_ratio/4


def clss():
    os.system('cls' if os.name=='nt' else 'clear')
clss()













#compressor sections
compressor_inner_bot = make_circle(0, section_radius, offset=0)

shape = (lambda u, section_radius1, section_radius2, section_height: (section_radius2 - section_radius1) * (u) / section_height )
for i in range(sections_amount):
	section_radius1 = section_radius * section_blade_radius_increment_ratio**(sections_amount-i)
	section_radius2 = section_radius * section_blade_radius_increment_ratio**(sections_amount-i-1)
	section_blades = int((section_radius*2*math.pi) / section_blade_density )
	attach.append({"blades":section_blades})
	attach_compressor.append({"blades":section_blades})
	# print(section_radius1, section_radius2)

	for q in range(section_blades):
		prop = make_propeller(section_radius, section_prop_radius_outer, section_blade_thickness, int(section_height/2), section_blade_angles[0], section_blade_angles[1], q, 
			offset=section_offset + i*section_height, blades = section_blades, shape_function=[shape, section_radius1, section_radius2, section_height] )
		attach[i] = {**attach[i] , **prop[1] }
		# propeller.append(prop[0])

		if i != sections_amount-1:
			stators = make_propeller(section_radius+1, compressor_radius, section_blade_thickness, int(section_height/2), section_stator_angles[0], section_stator_angles[1], q, 
				offset=section_offset + i*section_height + section_height/2, blades = 1, reversed=1 )
			attach_compressor[i] = {**attach_compressor[i] , **stators[1] }
			propeller.append(stators[0])


	if i == sections_amount-1:
		section_height_2 = int(section_height/2)

	# cylinder, section_radius = make_cylinder( section_radius, section_height_2, offset=section_offset + i*section_height, shape_function=shape, attachment_points = attach[i] 
	# 	)
	# sections.append( cylinder )

	if i != sections_amount-1:
		cylinder = make_cylinder( compressor_radius, section_height_2, offset=section_offset + i*section_height, flip=1, attachment_points = attach_compressor[i], reversed=True)
		sections.append(cylinder)


	rod1_offset = section_offset + i*section_height + section_height_2



#propellers
attach.append({"blades":blades})
for i in range(blades):
	prop = make_propeller(cylinder_radius, blade_radius, blade_thickness, cylinder_height, blade_angles[0], blade_angles[1], i, offset=cylinder_offset , blades = blades)
	attach[-1] = {**attach[-1] , **prop[1] }
	# propeller.append(prop[0])

#hyperfan
# cylinder = make_cylinder(cylinder_radius, cylinder_height, offset=cylinder_offset, attachment_points = attach[-1])
# cylinder_bot = make_circle(rod1_radius, cylinder_radius, offset=cylinder_offset)
# cylinder_top = make_circle(0, cylinder_radius, offset=cylinder_height+cylinder_offset, flip=1)

#rod
rod = make_cylinder(rod1_radius, rod1_height, offset = rod1_offset)
rod_top = make_circle(0, rod1_radius, offset = rod1_offset+rod1_height, flip=1)
rod_bot = make_circle(rod1_radius, section_radius, offset = rod1_offset, flip=1)

#duct
duct_inner = make_cylinder(blade_radius+duct_gap, duct_height, offset=duct_offset, flip=1)
duct_outer = make_cylinder(blade_radius+duct_gap+duct_thickness, duct_height, offset=duct_offset)
# duct_bot = make_circle(blade_radius+duct_gap, blade_radius+duct_gap+duct_thickness, offset=duct_offset)
duct_top = make_circle(blade_radius+duct_gap, blade_radius+duct_gap+duct_thickness, offset=duct_offset+duct_height, flip=1)


#compressor tube
# compressor_tube_inner = make_cylinder(compressor_radius, compressor_height, offset=compressor_offset, flip=1)
compressor_tube_outer = make_cylinder(compressor_radius+compressor_thickness, compressor_height, offset=compressor_offset)
compressor_tube_bot = make_circle(compressor_radius, compressor_radius+compressor_thickness, offset=compressor_offset)
compressor_tube_top = make_circle(compressor_radius, compressor_radius+compressor_thickness, offset=compressor_offset+compressor_height, flip=1)

#starting points
# combined = numpy.append(cylinder_bot, cylinder_top)
# combined = numpy.append(duct_inner, duct_outer)
combined = numpy.append(rod, rod_top)

#compressor inner part
for i in sections:
	combined = numpy.append(combined, i)
combined = numpy.append(combined, compressor_inner_bot)

#hyperfan
for i in propeller:
	combined = numpy.append(combined, i)
# combined = numpy.append(combined, cylinder)

#rod
# combined = numpy.append(combined, rod_top)
# combined = numpy.append(combined, rod)
# combined = numpy.append(combined, rod_bot)

#duct
# combined = numpy.append(combined, duct_inner)
# combined = numpy.append(combined, duct_outer)
# combined = numpy.append(combined, duct_top)
# # combined = numpy.append(combined, duct_bot)

#compressor
# combined = numpy.append(combined, compressor_tube_inner)
# combined = numpy.append(combined, compressor_tube_outer)
# combined = numpy.append(combined, compressor_tube_bot)
# combined = numpy.append(combined, compressor_tube_top)


combined = mesh.Mesh(combined)

combined.save(filename="test.stl")

# os.system('{}\\test.stl'.format(os.getcwd()))

