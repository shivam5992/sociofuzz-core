def get_stars(i):
	a = '<i class="fa fa-star fstar"></i>'
	a1 = '<i class="fa fa-star-half-o fstar"></i>'
	b = '<i class="fa fa-star sstar"></i>'
	b1 = '<i class="fa fa-star-half-o sstar"></i>'
	c = '<i class="fa fa-star tstar"></i>'
	c1 = '<i class="fa fa-star-half-o tstar"></i>'
	d = '<i class="fa fa-star frstar"></i>'
	d1 = '<i class="fa fa-star-half-o frstar"></i>'
	e = '<i class="fa fa-star fvstar"></i>'
	e1 = '<i class="fa fa-star-half-o fvstar"></i>'
	f = '<i class="fa fa-star-o fvstar"></i>'

	stat = ""
	if i >= 0 and i < 1:
		stat = a1 + f + f + f + f
		kw = 'Must Avoide'
	elif i >= 1 and i < 2:
		stat = a + f + f + f + f
		kw = 'Avoidable'
	elif i >= 2 and i < 3:
		stat = a + b1 + f + f + f
		kw = 'Avoidable'
	elif i >= 3 and i < 4:
		stat = a + b + f + f + f
		kw = 'Below Average'
	elif i >= 4 and i < 5:
		stat = a + b + c1 + f + f
		kw = 'Below Average'
	elif i >= 5 and i < 6:
		stat = a + b + c + f + f
		kw = 'Average'
	elif i >= 6 and i < 7:
		stat = a + b + c + d1 + f
		kw = 'Average'
	elif i >= 7 and i < 8:
		stat = a + b + c + d + f
		kw = 'Recommended'
	elif i >= 8 and i < 9:
		stat = a + b + c + d + e1
		kw = 'Must Watch'
	elif i >= 9 and i <= 10:
		stat = a + b + c + d + e
		kw = 'All Time Great'
	return stat, kw