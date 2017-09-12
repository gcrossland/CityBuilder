import os.path
execfile(os.path.dirname(pathName) + "/02 cities C.py")
endpoints[:] = [tuple(reversed(e)) for e in endpoints]
