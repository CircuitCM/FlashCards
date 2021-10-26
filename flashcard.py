from typing import Union
from PIL.Image import Image
import io

class FlashCard(object):

    class CardError(Exception):

        def __init__(self,message):
            super(FlashCard.CardError, self).__init__(message)

    def __init__(self,name:str):
        self.name = name
        self.ques:list[str]=[]
        self.ans:list[str]=[]

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


