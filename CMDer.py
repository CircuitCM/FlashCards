import sys
import traceback as tb
import colorama
import termcolor
from typing import Union

def python_slash(pth: str) -> str:
    chry: [chr] = [ch for ch in pth]
    for i in range(0, len(chry)):
        if chry[i] == '\\':
            chry[i] = '/'
    return ''.join(chry)


def gp(msg, i:int=1):
    clr = 'red'
    if i == 1:
        clr = 'green'
    elif i == 2:
        clr = 'yellow'
    print(termcolor.colored(msg, clr))


def conv_bool(s:str):
    s = s.lower()
    sl = len(s)
    if sl <= 5 and s == 'false'[:sl]:return False
    elif sl <= 4 and s == 'true'[:sl]:return True
    else: raise ValueError


_CMD_DICT: dict[str,Union[tuple, dict]]= {}


def command(path: list[str]=None, argtypes:tuple=(), argmin:int=0, argmax:int=0):
    if argmax == 0: argmax = len(argtypes)
    def _deco(func):
        pt=path
        fn = func.__name__
        if pt is None:
            pt = ['']
        ipt = iter(pt)
        np:str = next(ipt,None)
        dl = _CMD_DICT
        while np is not None:
            if np is '' or np is ' ':np=fn
            v:Union[dict,tuple] = dl.get(np, None)
            np1: str = next(ipt, None)
            if v is None:
                #np1 = next(ipt,None)
                if np1 is None:
                    dl[np]=(func,argtypes,argmin,argmax)
                    gp(f'Command: { " ".join(pt)} {argtypes}, added.',1)
                else:
                    nd: dict[str,Union[tuple, dict]] = {}
                    dl[np]=nd
                    dl=nd
            else:
                vt = type(v)
                #np1 = next(ipt, None)
                if vt is tuple:
                    if np1 is None:
                        gp(f'Command: { " ".join(pt)}, already exists skipping.',2)
                    else:
                        nd = {'': v}
                        dl[np]=nd
                        dl=nd
                elif np1 is None:
                    vtp = v.get('',None)
                    if vtp is None:
                        v['']=(func,argtypes,argmin,argmax)
                        gp(f'Command: {" ".join(pt)} {argtypes}, added.', 1)
                    else:
                        gp(f'Command: {" ".join(pt)}, already exists skipping.',2)
                else:
                    dl=v
            np=np1
    return _deco


def try_conversions(vr:str,typ:tuple,i:int):
    if i>= len(typ): return vr
    elif typ[i]==bool: return conv_bool(vr)
    else: return typ[i](vr)


def tryfunc(cls: list, ft:tuple):
    cml = len(cls)
    if not (ft[2] <= cml <= ft[3]):
        gp('Incorrect amount of arguments.',3)
    else:
        if cml>0:
            try:
                cls = [try_conversions(vr,ft[1],i) for vr,i in zip(cls,range(0,cml))]
            except:
                gp('Incorrect argument types, make sure arguments are inputted correctly.', 3)
                return
        try:
            return ft[0](*cls)
        except:
            gp(tb.format_exc()+"\nYou might have used an incorrect argument for this command.",3)


def find_cmd(cmds: list[str], cd: dict):
    #gp(cmds)
    cc = len(cmds)
    cmd= cmds[0]
    cl= len(cmd)
    cls = [*filter(lambda k: cmd==k[:cl],cd.keys())]
    l = len(cls)
    if l == 1:
        #gp('len is one')
        ncd = cd.get(cls[0])
        if type(ncd) is dict:
            #gp('found dict instance')
            return find_cmd(cmds[1:]if cc>1 else ['-NULL'],ncd)
        else:
            #gp('found cmd instance')
            #remember this change -------\/
            return tryfunc(cmds[1:]if cc>0 else [],ncd)
    elif l<1:
        #gp('cmd not recognized trying default cmd',2)
        fnc = cd.get('',None)
        if fnc is not None:
            #gp('there is default cmd')
            return tryfunc(cmds[1:]if cc>0 else [],fnc)
    gp("Couldn't identify command.", 3)


_SBREAKS = {'`','"',"'"}

def _min_k(bp:dict,ltx:int):
    minv = ltx
    mink = None
    for k, v in bp.items():
        if len(v[1])>v[0]+1:
            p = v[1][v[0]]
            if minv>p:
                minv=p
                mink=k
    return mink, minv


def _quote_breaker(tx:str):
    bp = {s:[0,[]] for s in _SBREAKS}
    ltx= len(tx)
    for n, i in filter(lambda m: m[0] in _SBREAKS, zip(tx,range(0,ltx))):
        bp[n][1].append(i)
    mink, minv = _min_k(bp,ltx)
    intrv=[]
    while mink is not None:
        ml = bp[mink]
        nv = ml[1][ml[0]+1]
        intrv.append((minv,nv))
        for k,v in filter(lambda n: n[0]!=mink, bp.items()):
            while v[0]<len(v[1]) and v[1][v[0]]<nv:
                v[0]+=1
        ml[0]+=2
        mink, minv = _min_k(bp, ltx)
    return intrv


def _get_request(cmds:dict, tx:str):
    if tx=='':return None
    pts = _quote_breaker(tx)
    #print(pts)
    #if len(pts)==0: return _find_cmd([*filter(lambda x: x!='', tx.split(' '))],cmds)
    cms = []
    st=0
    for s,e in pts:
        cms.extend(tx[st:s].split(' '))
        cms.append(tx[s+1:e])
        st=e+1
    cms.extend(tx[st:len(tx)].split(' '))
    return find_cmd([*filter(lambda x: x != '', cms)],cmds)


_EXIT= False


def exit():
    global _EXIT
    _EXIT = True


command(['echo'],(str,int),1,2)(gp)
command(['exit'])(exit)


def start_cmdline(name:str=''):
    colorama.init(True)
    while not _EXIT:
        _get_request(_CMD_DICT,input(name))
    sys.exit()