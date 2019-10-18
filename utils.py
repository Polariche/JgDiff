def url_args(d):
    return '?'.join([''] + [x[0].__str__()+'='+x[1].__str__() for x in list(d.items())])