import termcolor
import os

_PFL = '.p'

def python_slash(pth: str) -> str:
    chry: [chr] = [ch for ch in pth]
    for i in range(0, len(chry)):
        if chry[i] == '\\':
            chry[i] = '/'
    return ''.join(chry)


def global_print(msg, i:int=1):
    clr = 'red'
    if i == 1:
        clr = 'green'
    elif i == 2:
        clr = 'yellow'
    print(termcolor.colored(msg, clr))

gp = global_print


def get_pickled_files(dr):
    #assume ctd is small
    return [*filter(lambda x: x[-len(_PFL):]==_PFL,os.listdir(dr))]

def self_pickled_files(nl:list,dr):
    return nl.extend(dr+i for i in filter(lambda x: x[-len(_PFL):] == _PFL, os.listdir(dr)))


def try_mkdir(dr):
    try:
        os.mkdir(dr)
        return True
    except: return False


def rm_dir(dir,rm_base=True,only_dirs=False):
    if not os.path.exists(dir): return 0
    fls=False
    for r, d, f in os.walk(dir,False):
        if not only_dirs:
            for files in f:
                os.remove(os.path.join(r, files))
        elif not fls and len(f)>0:fls=True
        os.removedirs(r)
    if rm_base:try_os_rm(dir)
    return 1 if only_dirs else 2 if fls else 1

def walk_all_pickled_files(dr):
    drl=[]
    for r, d, f in os.walk(dr,False):
        for files in f:
            if len(files)>2 and files[-2:]=='.p':
                drl.append(os.path.join(r, files).replace('\\','/'))
    return drl



def try_os_rm(dr):
    try:
        os.remove(dr)
        return True
    except: return False
