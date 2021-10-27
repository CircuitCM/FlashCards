from PIL import Image
import d3dshot
from pynput import mouse,keyboard
from pynput.mouse import Controller, Button
import flashcard as fl
from misc import gp


MOUSE_POS1=(0,0)
IS_CONTROL=False
IS_ACTIVE=False
IS_QUES=False

def launch():
    global mcon,d3d
    mcon = Controller()
    #capture_output=1
    d3d = d3dshot.create()
    kl = keyboard.Listener(on_press=key_press, on_release=key_release)
    kl.start()
    kl.join()

def key_press(key):
    try:
        n = key.__dict__.get('_name_',None)
        global IS_CONTROL,mcon,d3d,MOUSE_POS1,IS_ACTIVE,IS_QUES
        if n=='ctrl_l':
            IS_CONTROL=True
        if IS_CONTROL:
            if n=='alt_l':
                MOUSE_POS1=mcon.position
            elif n=='cmd':
                if fl.CARD is not None:
                    x,y = mcon.position
                    if x<MOUSE_POS1[0]:nx,mx=x,MOUSE_POS1[0]
                    else:mx,nx=x,MOUSE_POS1[0]
                    if y<MOUSE_POS1[1]:ny,my=y,MOUSE_POS1[1]
                    else:my,ny=y,MOUSE_POS1[1]
                    bbx=(int(nx),int(ny),int(mx),int(my))
                    img: Image.Image = d3d.screenshot(region=bbx)
                    img=img.convert('RGB',dither=3,colors=16)
                    #fn = lambda x: 255 if x > 180 else 0
                    fl.CARD._add(img,IS_QUES)
                    #img = img.point(lambda x: 255 if x > 180 else 0, mode='1')
                    gp(f'Image added to {"questions" if IS_QUES else "answers"}')
                else: gp('No pdf available, image not saved.',2)
            elif n=='shift':
                IS_QUES= not IS_QUES
                gp(f'Toggled {"questions" if IS_QUES else "answers"}')
    except Exception as e:
        gp(e,3)


def key_release(key):
    n = key.__dict__.get('_name_', None)
    global IS_CONTROL
    if n == 'ctrl_l':
        IS_CONTROL=False





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
