
import time

import flashcard as fl
from flashcard import FlashCard
import fastcapture
from misc import gp, try_mkdir, rm_dir, try_os_rm,_PFL,get_pickled_files,os
from CMDer import command,start_cmdline
from threading import Thread



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
    fl.CURDR=fl.CURDR[:fl.CURDR.rfind('/')+1]
    show_section()


def leave_sections():
    fl.CURDR=fl.FLDIR
    show_section()


def show_section():
    gp(f'In Section:\n*/{fl.CURDR[len(fl.CDIR):]}')

def show_dir():
    gp('\n'.join(os.listdir(fl.CURDR)))


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
        gp(i)


def show_ans():
    for i in fl.CARD.ans:
        gp(i)


def launch_memorizer():
    import sys
    import subprocess
    #print(f'{sys.executable} {fl.CDIR}memorizer.py')
    subprocess.Popen(f'{sys.executable} {fl.CDIR}memorizer.py',shell=True)
    time.sleep(.2)
    sys.exit()



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
    start_cmdline()




