from django.http import JsonResponse

def json_response(status, data=None, error=None):
    return JsonResponse({
        "status": status,
        "data": data,
        "error": error
    })


def toCamelCase(string):
	if '_' not in string:
		return string
	orig = string
	pos = []
	while True:
		position = string.find('_') + 1
		pos.append(position)
		string = string[position:]
		if '_' not in string:
			break
	string = orig
	for p in pos:
		string = string[0:p] + string[p].upper() + string[p+1:]
	del orig
	return string.replace('_', '')
