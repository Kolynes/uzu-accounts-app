import random

def generate_code(length):
	code = ''
	random.seed()
	for x in range(length):
		code += random.choice(
			[
				chr(random.choice(range(26)) + 0x41),
				chr(random.choice(range(26)) + 0x61),
				chr(random.choice(range(10)) + 0x30),
			]
		)
	return code

def generate_number_code(length):
	code = ""
	random.seed()
	for x in range(length):
		code += chr(random.choice(range(10)) + 0x30)
	return code
