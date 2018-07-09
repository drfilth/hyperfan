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


def make_cylinder(radius, height, offset=0, attachment_points = None, shape_function=None, flip=0, reversed=False):
	omkreds = math.ceil(2*radius*math.pi)
	omkreds_rounded = math.ceil(omkreds)
	triangles= omkreds_rounded*2
	rotation = 0

	data = numpy.zeros(triangles*height*2, dtype=mesh.Mesh.dtype)
	triangle = 0
	isbetween, isbetween_temp = False, False

	iterator = range(height)
	if reversed:
		iterator = range(height,0,-1)

	for u in iterator:
		if shape_function:
			radius1 = radius - shape_function[0](u, shape_function[1], shape_function[2], shape_function[3])
			radius2 = radius - shape_function[0](u+1, shape_function[1], shape_function[2], shape_function[3])
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
			radius3 = radius1 - shape_function[0](u+1, shape_function[1], shape_function[2], shape_function[3])
			radius1_1 = radius1 - shape_function[0](u, shape_function[1], shape_function[2], shape_function[3])
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

			if reversed==0:
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
				propeller_attachments["{}-{}-{}".format(prop,u,t)].append([
											vector[0],
											vector[1]
										])

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
			radius1_1 = radius1 - shape_function[0](chord*t, shape_function[1], shape_function[2], shape_function[3])

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
