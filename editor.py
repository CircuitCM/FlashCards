
import flashcard as fl
from flashcard import FlashCard
import fastcapture
from misc import gp, try_mkdir, rm_dir, try_os_rm,_PFL,os,walk_all_pickled_files
from CMDer import command,start_cmdline
from threading import Thread
from PIL import Image
import re
import psutil


#for proper sorting we assume that all cards have the same directory depth
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
        fl.update_show_perf_metrics()
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

def kill_displayed_imgs():
    #psutil.test()
    for proc in psutil.process_iter():
        n=proc.name()
        #gp(proc.cmdline())
        if n in "display" or n in 'Microsoft.Photos.exe':
            gp(f'Killing: {n}')
            proc.kill()

def next_fix():
    if len(fl.dups)==0:
        gp('No cards to be fixed were found, try refreshing fix.',2)
    else:
        ind = 'None'
        if len(fl.CARD.ans) != 0 or len(fl.CARD.ques) != 0:
            ind = fl.save_flcard(fl.CURDR, fl.CARD)
        ps= fl.dups.pop(0)
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

t_imshow=False

def next_withimgs():
    if len(fl.all_imgs)==0:
        gp('No cards with images found, try refreshing cards with images.',2)
    else:
        if t_imshow: kill_displayed_imgs()
        ind='None'
        if len(fl.CARD.ans) != 0 or len(fl.CARD.ques) != 0:
            ind = fl.save_flcard(fl.CURDR, fl.CARD)
        ps= fl.all_imgs.pop(0)
        dri= ps[:ps.rfind('/') + 1]
        if dri!=fl.CURDR:
            fl.CURDR=dri
            show_section()
        fl.CARD = fl.load_flcard(ps)
        gp(f'Saved last flashcard to index: {ind} and got next image containing card: {ps}')
        gp('Questions:')
        show_ques()
        gp('Answers:')
        show_ans()
        if t_imshow:
            show_all_img()

def toggle_imgcardshow():
    global t_imshow
    t_imshow = not t_imshow
    gp(f'Images display {"on" if t_imshow else "off"} in image card iterator.')

def show_fix():
    gp('\n'.join(fl.dups))

def show_cards_imgs():
    gp('\n'.join(fl.all_imgs))

def show_origin_ofdups():
    gp('\n'.join(fl.origin))

def count_total_flcards():
    gp(f'Total # of cards in section */{fl.CURDR[len(fl.CDIR):]}: {len(walk_all_pickled_files(fl.CURDR))}')

def show_all_img():
    imv = 0
    imh = 0
    imgs = []
    imvs = [0, ]
    for p in [*fl.CARD.ans, *fl.CARD.ques]:
        tf = type(p)
        if tf != str:
            icd = Image.open(p)
            nim = icd.resize((int(icd.size[0] * .35), int(icd.size[1] * .35)), Image.LANCZOS)
            sz = nim.size
            imv += sz[1]
            imgs.append(nim)
            imvs.append(imv)
            if imh < sz[0]: imh = sz[0]
    if imv>0:
        im = Image.new('RGB', (imh, imv), (255, 255, 255))
        for i,v in zip(imgs,imvs):
            im.paste(i,(0,v))
        im.show(title=f'*/{fl.CURDR[len(fl.CDIR):]}')
    else:
        gp(f'No images in card: */{fl.CURDR[len(fl.CDIR):]}',2)


def show_img_origin(pos:int,ques=False):
    #gp('image origin called')
    lk=fl.CARD.ques if ques else fl.CARD.ans
    i = lk[pos-1]
    if type(i)!=str:
        bf = i.getbuffer()
        bt = bf.nbytes
        gt = FlashCard.DUPIMS.get(bt, None)
        gp(f'Image origin: */{gt[len(fl.CDIR):]}')
        gp(f'Image current: */{f"{fl.CURDR}{fl.CARD.loaded_num}.p"[len(fl.CDIR):]}')
        if gt ==f'{fl.CURDR}{fl.CARD.loaded_num}.p':
            gp('Origin image is in this card.',2)
            return
        if gt is not None:
            ocd = fl.load_flcard(gt)
            for p in [*ocd.ans, *ocd.ques]:
                tf = type(p)
                if tf != str:
                    np=p
                    of = p.getbuffer()
                    ot = of.nbytes
                    if ot == bt: break
            else:
                gp('No origin image found',2)
                return
            Image.open(np).show(title=gt)
        else:
            gp('No origin image found', 2)
    else:
        gp(f'{"Question" if ques else "Answer"} at index: {i}, is not an image.',2)

def show_img(pos:int,ques=False):
    lk=fl.CARD.ques if ques else fl.CARD.ans
    i = lk[pos-1]
    if type(i)!=str:
        Image.open(i).show(title=fl.CURDR)
    else:
        gp(f'{"Question" if ques else "Answer"} at index: {i}, is not an image.',2)


if __name__ == '__main__':
    Thread(target=fastcapture.launch,daemon=True).start()
    command(['show', 'section'])(show_section)
    command(['go', 'section'], (str,), 1, 1)(go_section)
    command(['new', 'section'], (str,), 1, 1)(new_section)
    command(['back', 'section'])(back_section)
    command(['leave', 'sections'])(leave_sections)
    command(['toggle','fastcapture'],)(toggle_fastcapture)
    command(['delete','section'],(str,),0,1)(del_section)
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
    command(['restart'],)(fl.restart_performance)
    command(['restart', 'performance'],)(fl.restart_performance)
    command(['refresh','fix'],)(fl.refresh_image_duplicates)
    command(['refresh', 'imagecards'], )(fl.load_all_image_cards)
    command(['next', 'fix'])(next_fix)
    command(['next', 'imagecard'])(next_withimgs)
    command(['show','cards', 'fix'])(show_fix)
    command(['show', 'origin'])(show_origin_ofdups)
    command(['show', 'image', 'origin'], (int, bool), 1, 2)(show_img_origin)
    command(['show', 'image'],(int,bool),1,2)(show_img)
    command(['show','all', 'images'],)(show_all_img)
    command(['show', 'cards', 'images'])(show_cards_imgs)
    command(['close', 'images'],)(kill_displayed_imgs)
    command(['toggle', 'imagecards'], )(toggle_imgcardshow)
    command(['count'], )(count_total_flcards)
    command(['count', 'cards'], )(count_total_flcards)
    command(['count', 'imagecards'], )(lambda : gp(f'There are {len(fl.all_imgs)} unchecked cards with images.'))
    command(['count', 'fix'], )(lambda: gp(f'There are {len(fl.dups)} unchecked cards with possible duplicate images.'))
    start_cmdline()




