def url_args(d):
    return '&'.join([x[0].__str__()+'='+x[1].__str__() for x in list(d.items())] + [''])

def get(d, k):
	if k in d.keys():
		return d[k]
	else:
		return None