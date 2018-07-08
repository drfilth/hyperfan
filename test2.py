radius = 15

for i in range(5):
	for u in range(10):
		radius1 = radius * 0.75**i
		radius2 = radius * 0.75**(i+1)
		radius3 = (radius1 - radius2) * (u+1) / 10
		print(i, radius1, radius2, radius3)



