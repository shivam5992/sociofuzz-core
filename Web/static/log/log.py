data = open("DedhIshqiya").read().split("\n")

acts = {}
for i, line in enumerate(data):
	if "No Image for" in line:
		if line not in acts:
			acts[line] = 1
			# if len(line) > 20:
			print line
			