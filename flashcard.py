from typing import Union
from PIL.Image import Image
import io,os

class FlashCard(object):

    class CardError(Exception):

        def __init__(self,message):
            super(FlashCard.CardError, self).__init__(message)

    def __init__(self):
        self.ques:list[Union[str,Image]]=[]
        self.ans:list[Union[str,Image]]=[]

    def _add(self,itm:Union[Image,str],qus:bool=True):
        ls = self.ques if qus else self.ans
        match itm:
            case Image():
                with io.BytesIO() as bb:
                    itm.save(bb, 'jpeg', quality=60, optimize=True, subsampling=2)
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
        if index is None:
            del ls[-1]
        else:
            del ls[index]

    def remove_ques(self,indx:int):
        self._remove(indx,True)

    def remove_ans(self,indx:int):
        self._remove(indx,False)

def try_mkdir(dr):
    try:
        os.mkdir(dr)
        return True
    except:
        return False

def python_slash(pth: str) -> str:
    chry: [chr] = [ch for ch in pth]
    for i in range(0, len(chry)):
        if chry[i] == '\\':
            chry[i] = '/'
    return ''.join(chry)

CDIR = python_slash(__file__).rsplit('/', 1)[0]+'/'
FLDIR = CDIR+'flashcards/'
try_mkdir(FLDIR)
CARD:FlashCard=FlashCard()


