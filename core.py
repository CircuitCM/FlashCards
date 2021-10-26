import os
from CMDer import gp, python_slash

def try_mkdir(dr):
    try:
        os.mkdir(dr)
        return True
    except:
        return False


CDIR = python_slash(__file__).rsplit('/', 1)[0]+'/'
FLDIR = CDIR+'flashcards/'
try_mkdir(FLDIR)
IMGDISABLED=False