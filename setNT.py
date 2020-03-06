def set_nt(gas_name, temp) :
	nt = 0
	x = 0

	if (gas_name == 'no2') :
		return 1

	elif(gas_name == 'co') :
		x = temp
		termini = []
		termini.append(-1.289682539 * pow(10, - 11) * pow(x, 8))
		termini.append(9.424603166 * pow(10, -10) * pow(x, 7))
		termini.append(9.027777778 * pow(10, -9) * pow(x, 6))
		termini.append(-1.52361111 * pow(10, -6) * pow(x, 5))
		termini.append(2.777777763 * pow(10, -6) * pow(x, 4))
		termini.append(7.055555551 * pow(10, -4) * pow(x, 3))
		termini.append(1.144841276 * pow(10, -3) * pow(x, 2))
		termini.append(- 4.126190473 * pow(10, -2) * x)
		termini.append(6.999999997 * pow(10, -1))
		nt_temp= 0
		for term in termini:
			nt_temp+=term
		nt=round(nt_temp,10)
		return nt

	elif (gas_name == 'h2s') :
		return 1

	elif (gas_name == 'so2') :
		return 1

	elif (gas_name == 'o3') :
		x = temp
		termini = []
		termini.append(-3.968253966 * pow(10, - 13) * pow(x, 8))
		termini.append( 4.76190476 * pow(10, -11) * pow(x, 7))
		termini.append(-1.111111111 * pow(10, -9) * pow(x, 6))
		termini.append(-4.999999997 * pow(10, -8) * pow(x, 5))
		termini.append(2.305555555 * pow(10, -6) * pow(x, 4))
		termini.append(-1.666666689 * pow(10, -6) * pow(x, 3))
		termini.append(-7.19047619 * pow(10, -4) * pow(x, 2))
		termini.append(2.561904764 * pow(10, -2) * x)
		termini.append(1.3)
		nt_temp= 0
		for term in termini:
			nt_temp+=term
		nt=round(nt_temp,10)
		return nt


def main() :
	print(set_nt('o3',50))


if __name__ == '__main__' :
    main()