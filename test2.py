import math

angle = math.pi/6

radius = 15

for i in range(10):
	radius1 =  math.cos(angle) * i * radius
	radius2 =  math.cos(angle) * (i+1) * radius

	print(i, radius1, radius2)



