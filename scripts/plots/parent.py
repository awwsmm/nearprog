# very dumb / hacky way of importing files from parent directory
#import sys
#import os

#def relpath(path):
#    basedir = os.getcwd()
#    scriptpath = __file__
#    return os.path.abspath(os.path.join(basedir, scriptpath, '../', path))

## add the parent directory to the path, so we can access those files
#sys.path.insert(1, relpath('../'))