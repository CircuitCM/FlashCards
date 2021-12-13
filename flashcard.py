import re
from typing import Union
from PIL.Image import Image
from misc import get_pickled_files, _PFL, try_mkdir, os, walk_all_pickled_files, gp
import pickle
import io

class FlashCard(object):

    class CardError(Exception):

        def __init__(self,message):
            super(FlashCard.CardError, self).__init__(message)

    DUPIMS:dict={}

    def __init__(self):
        self.loaded_num:int = None
        self.ques:list[Union[str,io.BytesIO]]=[]
        self.ans:list[Union[str,io.BytesIO]]=[]
        self.pques=0
        self.pans=0

    def _add(self,itm:Union[Image,str],qus:bool=True):
        ls = self.ques if qus else self.ans
        match itm:
            case Image():
                bb =io.BytesIO()
                itm.save(bb, 'jpeg', quality=70, optimize=True, subsampling=2)
                bl=bb.getbuffer().nbytes
                fls=self.DUPIMS.get(bl,None)
                if fls is not None: gp(f'Warning this image was found in: {fls}.',2)
                ls.append(bb)
            case str():
                ls.append(itm)
            case _:
                raise self.CardError('Unkown Card Format.')

    def add_ques(self,itm):
        self._add(itm,True)

    def add_ans(self,itm):
        self._add(itm,False)

    def _remove(self,index:int=None,qus=True):
        ls = self.ques if qus else self.ans
        ln = len(ls) if index is None else index
        try:
            del ls[ln-1]
            return ln
        except:
            raise self.CardError('Index out of bounds.')

    def remove_ques(self,indx:int):
        return self._remove(indx,True)

    def remove_ans(self,indx:int):
        return self._remove(indx,False)



def python_slash(pth: str) -> str:
    chry: [chr] = [ch for ch in pth]
    for i in range(0, len(chry)):
        if chry[i] == '\\':
            chry[i] = '/'
    return ''.join(chry)


def save_flcard(dr, flcrd:FlashCard):
    if flcrd.loaded_num is None:
        ctd = get_pickled_files(dr)
        flcrd.loaded_num = len(ctd)+1
    svn = f'{dr}{flcrd.loaded_num}{_PFL}'
    with open(svn, 'wb+') as f:
        pickle.dump(flcrd, f)
    return flcrd.loaded_num


def load_flcard(dr,num:int=None):
    try:
        with open(f'{dr}{"" if num is None else str(num)+_PFL}','rb+') as f:
            fls = pickle.load(f)
        return fls
    except: return None


def refit_flcards(dr):
    pfl = get_pickled_files(dr)
    #as long as we just remove an indexed card it won't overwrite old ones, position of cards doesnt matter
    #only what card we'd like to remove
    for i, n in zip(range(1, len(pfl) + 1), pfl):
        os.renames(f'{dr}{n}',f'{dr}{i}{_PFL}')





CDIR = python_slash(__file__).rsplit('/', 1)[0]+'/'
FLDIR = CDIR+'flashcards/'
try_mkdir(FLDIR)
CURDR=FLDIR
CARD:FlashCard=FlashCard()

_ds=re.compile('\d+')
def _dirsort(k:str):
    r=0
    ks=k.split('/')
    for vs,mv in zip(ks,range(len(ks),0,-1)):
        v=_ds.findall(vs)
        if len(v)==0: continue
        v=int(v[0])
        r+=v*(1000**mv)
    return r

def _load_duplicate_cards():
    pf = walk_all_pickled_files(FLDIR)
    # gp(pf)
    pf.sort(key=_dirsort)
    FlashCard.DUPIMS.clear()
    for i in pf:
        fls = load_flcard(i)
        if fls is not None:
            for p in [*fls.ques, *fls.ans]:
                tp = type(p)
                if tp != str:
                    bt = p.getbuffer().nbytes
                    if bt not in FlashCard.DUPIMS:
                        FlashCard.DUPIMS[bt] = i

_load_duplicate_cards()


