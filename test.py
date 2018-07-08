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

def myround(x, base=5, errormargin=0):
	return_temp = base * float(x)/base
	if return_temp %0.25 < errormargin:
		return_temp = 0.25
	return return_temp

def between(n1, n2, n3, angle=0):
	if angle in [1/4,2/4,3/4]:
		if abs(n3) > abs(n1) and abs(n3) > abs(n2):
			return True
	if n1 <= n3 and n2 > n3:
		return True
	if n1 >= n3 and n2 < n3:
		return True
	return False

def sqrt(number):
	if number < 0:
		return -math.sqrt(abs(number))
	else:
		return math.sqrt(number)

def flip_orientation(flippingvector, indexes=[0,1,2]):
	temp_vector = [[],[],[]]
	temp_vector[indexes[0]] = flippingvector[indexes[1]]
	temp_vector[indexes[1]] = flippingvector[indexes[0]]
	temp_vector[indexes[2]] = flippingvector[indexes[2]]
	return temp_vector

def rotate_vector(vector, angle):
	#x' = x cos θ − y sin θ
	#y' = x sin θ + y cos θ
	for b in range(len(vector)):
		x = vector[b][0]
		y = vector[b][1]
		vector[b][0] = x*math.cos(angle) - y * math.sin(angle)
		vector[b][1] = x*math.sin(angle) + y * math.cos(angle)
	return vector


def make_cylinder(radius, height, offset=0, attachment_points = None, shape_function=None, flip=0):
	omkreds = math.ceil(2*radius*math.pi)
	omkreds_rounded = math.ceil(omkreds)
	triangles= omkreds_rounded*2
	rotation = 0

	data = numpy.zeros(triangles*height*2, dtype=mesh.Mesh.dtype)
	triangle = 0
	isbetween, isbetween_temp = False, False

	for u in range(height):
		if shape_function:
			radius1 = radius - shape_function(u, section_radius1, section_radius2, section_height)
			radius2 = radius - shape_function(u+1, section_radius1, section_radius2, section_height)
		else:
			radius1 = radius
			radius2 = radius
		u = u
		for i in range(0, omkreds_rounded):
			degree1 = 2*sympy.pi/omkreds*i
			degree2 = 2*sympy.pi/omkreds*(i+1)
			if i == omkreds_rounded-1:
				degree2 = 0

			x1 = radius1*math.cos( degree1 )
			y1 = radius1*math.sin( degree1 )
			z1 = u+offset

			x2 = radius1*math.cos( degree2 )
			y2 = radius1*math.sin( degree2 )
			z2 = u+offset

			x3 = radius2*math.cos( degree1 )
			y3 = radius2*math.sin( degree1 )
			z3 = u+1+offset

			x4 = radius2*math.cos( degree2 )
			y4 = radius2*math.sin( degree2 )
			z4 = u+1+offset

			vector = [
						[x1, y1, z1],
						[x2, y2, z2],
						[x3, y3, z3]
					]
			if flip != 0:
				vector = flip_orientation(vector)

			data["vectors"][triangle] = numpy.array(vector)
			triangle += 1


			vector = [
						[x2, y2, z2],
						[x4, y4, z4],
						[x3, y3, z3]
					]
			if flip != 0:
				vector = flip_orientation(vector)
			data["vectors"][triangle] = numpy.array(vector)
			triangle += 1


			if attachment_points != None:
				if u >= attachment_points["height"]:
					continue
				if rotation == attachment_points["blades"]:
					rotation=0
				isbetween_temp = False
				rotary_angle_2 = myround((1/omkreds)*(i+1), 0.01, 1/omkreds)
				if i == 0:
					rotary_angle_2 = 0.25

				a_u = attachment_points["{}-{}-0".format(rotation,u)][0]
				attach_x1 = a_u[0][0]
				attach_y1 = a_u[0][1]
				attach_x3 = a_u[1][0]
				attach_y3 = a_u[1][1]

				# anden attachment
				a_u = attachment_points["{}-{}-1".format(rotation,u)][0]
				attach_x2 = a_u[0][0]
				attach_y2 = a_u[0][1]
				attach_x4 = a_u[1][0]
				attach_y4 = a_u[1][1]

				#attachment til næste level
				try:
					a_u = attachment_points["{}-{}-1".format(rotation,u+1)][0]
					attach_y5 = a_u[1][1]
				except:
					attach_y5 = 0

				if between(x1, x2, attach_x1, rotary_angle_2) and between(y1, y2, attach_y1, rotary_angle_2):
					data["vectors"][triangle-2][1][0] = attach_x1
					data["vectors"][triangle-2][1][1] = attach_y1

					data["vectors"][triangle-1][0][0] = attach_x1
					data["vectors"][triangle-1][0][1] = attach_y1
					if between(x3, x4, attach_x3, rotary_angle_2) and between(y3, y4, attach_y3, rotary_angle_2):
						data["vectors"][triangle-1][1][0] = attach_x3
						data["vectors"][triangle-1][1][1] = attach_y3
					else:
						vector[0][0] = attach_x1
						vector[0][1] = attach_y1
						vector[1][0] = attach_x3
						vector[1][1] = attach_y3
						vector[2][0] = x4
						vector[2][1] = y4

						data["vectors"][triangle] = vector
						triangle+=1

					isbetween = True
					isbetween_temp = True



				#højre side
				if between(x3, x4, attach_x4, rotary_angle_2) and between(y3, y4, attach_y4, rotary_angle_2):
					data["vectors"][triangle-2][2][0] = attach_x4
					data["vectors"][triangle-2][2][1] = attach_y4

					data["vectors"][triangle-1][2][0] = attach_x4
					data["vectors"][triangle-1][2][1] = attach_y4

					if between(x3, x4, attach_x2, rotary_angle_2) and between(y3, y4, attach_y2, rotary_angle_2):
						data["vectors"][triangle-2][0][0] = attach_x2
						data["vectors"][triangle-2][0][1] = attach_y2
					else: 
						vector[0][0] = attach_x2
						vector[0][1] = attach_y2
						vector[2][0] = attach_x4
						vector[2][1] = attach_y4
						vector[1][0] = x1
						vector[1][1] = y1
						vector[1][2] = z1

						data["vectors"][triangle] = vector
						triangle+=1


					isbetween = False
					rotation += 1
					if i == omkreds_rounded-1 and attach_y5 > 0:
						rotation += -1

				#når en ny linje laves, kan der opstå en extra firkant fordi isbetween bliver sat til false på linjeskift. dette tjekker om firkanten er imellem.
				if i == 0 and between(attach_y3, attach_y4, y4 , 0.12):
					isbetween = True

				if isbetween and not isbetween_temp :
					triangle += -2

	if not shape_function:
		return data
	return data, radius2

def make_circle(radius1, radius2, offset=0, flip=0):
	omkreds1 = math.ceil(2*radius1*math.pi)
	if omkreds1 == 0:
		omkreds1 = 1
	omkreds2 = math.ceil(2*radius2*math.pi)
	omkreds2_rounded = math.ceil(omkreds2)
	triangles = omkreds2_rounded*2*2

	data = numpy.zeros(triangles*2, dtype=mesh.Mesh.dtype)
	triangle = 0

	old_u = -1
	for i in range(0, omkreds2_rounded):
		u = math.floor(omkreds1/omkreds2*i)

		degree1 = 2*sympy.pi/omkreds1*u
		degree2 = 2*sympy.pi/omkreds1*(u+1)
		degree3 = 2*sympy.pi/omkreds2*i
		degree4 = 2*sympy.pi/omkreds2*(i+1)

		if i == omkreds2_rounded-2:
			degree2=0

		if i == omkreds2_rounded-1:
			degree2=0
			degree4=0

		x1 = radius1*math.cos( degree1 )
		y1 = radius1*math.sin( degree1 )
		z1 = offset

		x2 = radius1*math.cos( degree2 )
		y2 = radius1*math.sin( degree2 )
		z2 = offset


		x3 = radius2*math.cos( degree3 )
		y3 = radius2*math.sin( degree3 )
		z3 = offset

		x4 = radius2*math.cos( degree4 )
		y4 = radius2*math.sin( degree4 )
		z4 = offset

		vector = [
					[x1, y1, z1],
					[x2, y2, z2],
					[x3, y3, z3]
				]
		if flip != 0:
			vector = flip_orientation(vector)
		data["vectors"][triangle] = numpy.array(vector)
		triangle += 1

		if radius1==0:
			triangle += -1

		if u==old_u and radius1 !=0 :
			triangle += -1

		vector = [
					[x2, y2, z2],
					[x4, y4, z4],
					[x3, y3, z3]
				]
		if flip != 0:
			vector = flip_orientation(vector)
		data["vectors"][triangle] = numpy.array(vector)
		triangle += 1

		old_u = u

	return data

def make_propeller(radius1,radius2,thickness,chord,degree1,degree2, prop, offset=0, blades=1, shape_function=None, reversed=0):
	propeller_attachments = {"height":chord}
	degree3 = 2/blades*prop*sympy.pi
	data = numpy.zeros(chord*2*2*2*2, dtype=mesh.Mesh.dtype)
	triangle = 0

	for u in range(chord):
		if shape_function:
			radius3 = radius1 - shape_function(u+1, section_radius1, section_radius2, section_height)
			radius1_1 = radius1 - shape_function(u, section_radius1, section_radius2, section_height)
		else:
			radius3 = radius1
			radius1_1 = radius1
		radius4 = radius2

		for t in range(2):
			# radius1
			y1 = (u+thickness[1]*t*2)*math.tan(degree1) 
			x1 = sqrt(radius1_1**2 - y1**2) 
			z1 = u+offset

			y3 = (u+1+thickness[1]*t*2)*math.tan(degree1) 
			x3 = sqrt( radius3**2 - y3**2) 
			z3 = u+1+offset

			# radius2
			a = (u+thickness[0]*t)*math.tan(degree2)
			A = math.asin(a/radius2)

			y2 = radius2*math.sin(A)
			x2 = sqrt( radius2**2 - y2**2) 
			z2 = u+offset

			a = (u+1+thickness[0]*t)*math.tan(degree2)
			A = math.asin(a/radius4)

			y4 = radius4*math.sin(A) 
			x4 = sqrt( radius4**2 - y4**2 )
			z4 = u+1+offset

			vector = [
						[x1, y1, z1],
						[x2, y2, z2],
						[x3, y3, z3]
					]

			vector = rotate_vector(vector, degree3)

			if "{}-{}-{}".format(prop,u,t) not in propeller_attachments:
				propeller_attachments["{}-{}-{}".format(prop,u,t)] = []

			propeller_attachments["{}-{}-{}".format(prop,u,t)].append([
										vector[0],
										vector[2]
									])

			if t == 1:
				vector = flip_orientation(vector, [0,2,1])
			if reversed !=0:
				vector = flip_orientation(vector)


			data["vectors"][triangle] = numpy.array(vector)
			triangle += 1



			vector = [
						[x2, y2, z2],
						[x4, y4, z4],
						[x3, y3, z3]
					]
			vector = rotate_vector(vector, degree3)
			if t == 1:
				vector = flip_orientation(vector)
			if reversed !=0:
				vector = flip_orientation(vector)

			data["vectors"][triangle] = numpy.array(vector)
			triangle += 1

		#edge
		radius_edge = radius2
		if reversed !=0:
			radius_edge = radius1

		a = (u+thickness[0]*0)*math.tan(degree2)
		A = math.asin(a/radius_edge)

		y1 = radius_edge*math.sin(A)
		x1 = sqrt( radius_edge**2 - y1**2) 
		z1 = u+offset

		a = (u+1+thickness[0]*0)*math.tan(degree2)
		A = math.asin(a/radius_edge)

		y3 = radius_edge*math.sin(A)
		x3 = sqrt( radius_edge**2 - y3**2 )
		z3 = u+1+offset


		a = (u+thickness[0]*1)*math.tan(degree2)
		A = math.asin(a/radius_edge)

		y2 = radius_edge*math.sin(A)
		x2 = sqrt( radius_edge**2 - y2**2) 
		z2 = u+offset

		a = (u+1+thickness[0]*1)*math.tan(degree2)
		A = math.asin(a/radius_edge)

		y4 = radius_edge*math.sin(A)
		x4 = sqrt( radius_edge**2 - y4**2 )
		z4 = u+1+offset

		vector = [
					[x1, y1, z1],
					[x2, y2, z2],
					[x3, y3, z3]
				]

		vector = rotate_vector(vector, degree3)
		data["vectors"][triangle] = numpy.array(vector)
		triangle += 1

		vector = [
					[x2, y2, z2],
					[x4, y4, z4],
					[x3, y3, z3]
				]
		vector = rotate_vector(vector, degree3)

		data["vectors"][triangle] = numpy.array(vector)
		triangle += 1

	#bottom and top
	for t in range(2):
		if shape_function:
			radius1_1 = radius1 - shape_function(chord*t, section_radius1, section_radius2, section_height)

		y1 = (t*chord+thickness[1]*2)*math.tan(degree1) 
		x1 = sqrt(radius1_1**2 - y1**2) 
		z1 = t*chord+offset

		y3 = (t*chord)*math.tan(degree1) 
		x3 = sqrt( radius1_1**2 - y3**2) 
		z3 = t*chord+offset

		# radius2
		a = (t*chord+thickness[0])*math.tan(degree2)
		A = math.asin(a/radius2)

		y2 = radius2*math.sin(A)
		x2 = sqrt( radius2**2 - y2**2) 
		z2 = t*chord+offset

		a = (t*chord)*math.tan(degree2)
		A = math.asin(a/radius2)

		y4 = radius2*math.sin(A) 
		x4 = sqrt( radius2**2 - y4**2 )
		z4 = t*chord+offset

		vector = [
					[x1, y1, z1],
					[x2, y2, z2],
					[x3, y3, z3]
				]

		vector = rotate_vector(vector, degree3)
		if t == 1:
			vector = flip_orientation(vector)
		if reversed !=0:
			vector = flip_orientation(vector)


		data["vectors"][triangle] = numpy.array(vector)
		triangle += 1

		vector = [
					[x2, y2, z2],
					[x4, y4, z4],
					[x3, y3, z3]
				]
		vector = rotate_vector(vector, degree3)
		if t == 1:
			vector = flip_orientation(vector)
		if reversed !=0:
			vector = flip_orientation(vector)


		data["vectors"][triangle] = numpy.array(vector)
		triangle += 1

	return data, propeller_attachments












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
			offset=section_offset + i*section_height, blades = section_blades, shape_function=shape )
		attach[i] = {**attach[i] , **prop[1] }
		# propeller.append(prop[0])

		if i != sections_amount-1:
			stators = make_propeller(section_radius+1, compressor_radius, section_blade_thickness, int(section_height/2), section_stator_angles[0], section_stator_angles[1], q, 
				offset=section_offset + i*section_height + section_height/2, blades = section_blades, reversed=1 )
			attach_compressor[i] = {**attach_compressor[i] , **stators[1] }
			propeller.append(stators[0])


	if i == sections_amount-1:
		section_height_2 = int(section_height/2)

	# cylinder, section_radius = make_cylinder( section_radius, section_height_2, offset=section_offset + i*section_height, shape_function=shape, attachment_points = attach[i] 
	# 	)
	# sections.append( cylinder )

	if i != sections_amount-1:
		cylinder = make_cylinder( compressor_radius, section_height_2, offset=section_offset + i*section_height, flip=1, attachment_points = attach_compressor[i])
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

