import math

angle = math.pi/10

radius = 15

for i in range(10):
	radius1 =  math.sin(angle) * radius * (i/10)
	radius2 =  math.sin(angle) * radius * ((i+1)/10)

	print(i, radius, radius1, radius2)



