import math

#x' = x cos θ − y sin θ
vector = [
	[25,5,0],
	[28,7,0],
	[30,4,0]
]

for i in vector:
	print(i[0]*math.cos(math.radians(90)) - i[1]*math.sin(math.radians(90)))
	print(i[0]*math.sin(math.radians(90)) + i[1]*math.cos(math.radians(90)))
	print()