
import time as t
import flashcard as fl
from flashcard import FlashCard
import fastcapture
from misc import gp, try_mkdir, rm_dir, try_os_rm,_PFL,os,walk_all_pickled_files
from CMDer import command,start_cmdline
from threading import Thread
from collections import deque
from PIL.Image import Image
import re

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


def go_section(name:str,check=True):
    if check:
        if name[-1] != '/': name = name + '/'
        if not os.path.isdir(f"{fl.CURDR}{name}"):
            gp("This section doesn't exist, make this section first.",3)
            return
    fl.CURDR=f"{fl.CURDR}{name}"
    show_section()


def new_section(name:str):
    if name[-1]!='/':name=name+'/'
    if not try_mkdir(f"{fl.CURDR}{name}"):
        gp('Section entered incorrectly or section already exists.',2)
    else:
        go_section(name,False)


def del_section(all_contents=False):
    out = rm_dir(fl.CURDR,only_dirs=not all_contents)
    if not out:
        gp("This section doesn't exist.",3)
        return
    if not all_contents:
        gp('Removed empty sections.')
        if out ==2:gp('There are still flashcards in this section.',2)
    else:
        gp("Deleted all sections and flashcards in them.")



def back_section():
    fl.CURDR=fl.CURDR[:fl.CURDR.rfind('/',0,-1)+1]
    show_section()


def leave_sections():
    fl.CURDR=fl.FLDIR
    show_section()


def show_section():
    gp(f'In Section:\n*/{fl.CURDR[len(fl.CDIR):]}')

def show_dir():
    ls=os.listdir(fl.CURDR)
    ls.sort(key=_dirsort)
    gp('\n'.join(ls))


def toggle_fastcapture():
    fastcapture.IS_ACTIVE=not fastcapture.IS_ACTIVE
    gp(f'Fast Capture is {"on" if fastcapture.IS_ACTIVE else "off"}.')


def delete_card(fla:int=None):
    if fla is None:
        fl.CURDR = FlashCard()
        gp('Reset current flashcard.')
    else:
        fln=f"{fl.CURDR}{fla}{_PFL}"
        if try_os_rm(fln):
            fl.refit_flcards(fl.CURDR)
            gp(f'Deleted flashcard #{fla} and adjusted flashcard index.')
        else: gp(f"Couldn't find flashcard at index: {fla}",2)


def next_card():
    if len(fl.CARD.ans) != 0 or len(fl.CARD.ques) != 0:
        ind = fl.save_flcard(fl.CURDR, fl.CARD)
        fl.CARD = FlashCard()
        gp(f'Saved flashcard to index: {ind} and moved to next flashcard.')
        update_show_perf_metrics()
    else:
        gp('Flashcard is already empty.',2)


def load_card(fla:int,save_cur=True):
    flc = fl.load_flcard(fl.CURDR,fla)
    if flc is None:
        gp(f"Couldn't find flashcard at index: {fla}",2)
    else:
        if save_cur and (len(fl.CARD.ans) != 0 or len(fl.CARD.ques) != 0):
            fl.save_flcard(fl.CURDR, fl.CARD)
            gp('Saving current flashcard')
        fl.CARD = flc
        gp(f'Loaded flashcard from index: {fla}')


def question(tx:str):
    fl.CARD.add_ques(tx)
    gp(f"Added text to question.")


def answer(tx:str):
    fl.CARD.add_ans(tx)
    gp(f"Added text to answer.")


def rm_ques(i:int=None):
    ni=fl.CARD.remove_ques(i)
    gp(f'Removed question at index: {ni}')


def rm_ans(i:int=None):
    ni=fl.CARD.remove_ans(i)
    gp(f'Removed answer at index: {ni}')


def show_ques():
    for i in fl.CARD.ques:
        if type(i)==str:
            gp(i)
        else:
            gp(f'Image with length: {i.getbuffer().nbytes}')


def show_ans():
    for i in fl.CARD.ans:
        if type(i) == str:
            gp(i)
        else:
            gp(f'Image with length: {i.getbuffer().nbytes}')


def launch_memorizer():
    import sys
    import subprocess
    #print(f'{sys.executable} {fl.CDIR}memorizer.py')
    subprocess.Popen(f'{sys.executable} {fl.CDIR}memorizer.py',shell=True)
    #t.sleep(.01)
    import CMDer
    CMDer._EXIT=True


AVG_T = [t.time(),0]
AVG_3 = deque(maxlen=4)
AVG_3.append(AVG_T[0])
AVG_10 = deque(maxlen=11)
AVG_10.append(AVG_T[0])

def restart_performance():
    AVG_T[0],AVG_T[1]=t.time(),0
    AVG_3.clear()
    AVG_3.append(AVG_T[0])
    AVG_10.clear()
    AVG_10.append(AVG_T[0])
    gp('Reset performance metrics')

def update_show_perf_metrics():
    now,CPH3,CPH10 = t.time(),0.,0.
    AVG_3.append(now), AVG_10.append(now)
    if len(AVG_3)>=4:
        lt = AVG_3.popleft()
        CPH3=3.*60.*60./(now-lt)
    if len(AVG_10)>=11:
        lt = AVG_10.popleft()
        CPH10=10.*60.*60./(now-lt)
    AVG_T[1]+=1
    TTL = AVG_T[1]*60.*60./(now-AVG_T[0])
    gp(f'Cards created: {AVG_T[1]}\nCPH 3 card: {int(CPH3*1000.)/1000.}\nCPH 10 card: {int(CPH10*1000.)/1000.}\nCPH total: {int(TTL*1000.)/1000.}')


dups= []
origin={}

def refresh_image_duplicates():
    global dups
    pf=walk_all_pickled_files(fl.FLDIR)
    #gp(pf)
    pf.sort(key=_dirsort)
    FlashCard.DUPIMS.clear()
    dups.clear()
    origin.clear()
    ubf=set()
    for i in pf:
        fls=fl.load_flcard(i)
        if fls is not None:
            for p in [*fls.ques,*fls.ans]:
                tp=type(p)
                if tp != str:
                    bt=p.getbuffer().nbytes
                    gt = FlashCard.DUPIMS.get(bt,None)
                    if gt is None:
                        FlashCard.DUPIMS[bt]=i
                    elif i not in ubf:
                        ubf.add(i)
                        origin[gt]=True
                        gp(f'Duplicate image(s) found in card: {i}, length: {bt}')
                        dups.append(i)

def next_fix():
    if len(dups)==0:
        gp('No cards to be fixed were found, try refreshing fix.')
    elif len(fl.CARD.ans) != 0 or len(fl.CARD.ques) != 0:
        ind = fl.save_flcard(fl.CURDR, fl.CARD)
        ps=dups.pop(0)
        dri= ps[:ps.rfind('/') + 1]
        if dri!=fl.CURDR:
            fl.CURDR=dri
            show_section()
        fl.CARD = fl.load_flcard(ps)
        gp(f'Saved last flashcard to index: {ind} and got next fix card: {ps}')
        gp('Questions:')
        show_ques()
        gp('Answers:')
        show_ans()
        #update_show_perf_metrics()
    else:
        gp('Flashcard is already empty.',2)


def show_fix():
    gp('\n'.join(dups))


def show_origin_ofdups():
    gp('\n'.join(origin))




if __name__ == '__main__':
    Thread(target=fastcapture.launch,daemon=True).start()
    command(['show', 'section'])(show_section)
    command(['go', 'section'], (str,), 1, 1)(go_section)
    command(['new', 'section'], (str,), 1, 1)(new_section)
    command(['back', 'section'])(back_section)
    command(['leave', 'sections'])(leave_sections)
    command(['toggle','fastcapture'],)(toggle_fastcapture)
    command(['delete','card'],(int,),0,1)
    command(['next', 'card'])(next_card)
    command(['load','card'],(int,bool),1,2)(load_card)
    command(['delete','card'],(int,),0,1)(delete_card)
    command(['question'],(str,),1,1)(question)
    command(['answer'],(str,),1,1)(answer)
    command(['remove','question'], (int,), 0, 1)(rm_ques)
    command(['remove','answer'], (int,), 0, 1)(rm_ans)
    command(['show', 'question'], (int,), 0, 1)(show_ques)
    command(['show', 'answer'], (int,), 0, 1)(show_ans)
    command(['launch','memorizer'])(launch_memorizer)
    command(['show', 'directory'])(show_dir)
    command(['restart'],)(restart_performance)
    command(['restart', 'performance'],)(restart_performance)
    command(['refresh','fix'],)(refresh_image_duplicates)
    command(['next', 'fix'])(next_fix)
    command(['show', 'fix'])(show_fix)
    command(['show', 'origin'])(show_origin_ofdups)
    start_cmdline()




