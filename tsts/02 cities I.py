import os.path
execfile(os.path.dirname(pathName) + "/02 cities D.py")
endpoints[:] = [tuple(reversed(e)) for e in endpoints]
