from PIL import Image
import d3dshot
from pynput import mouse,keyboard
from pynput.mouse import Controller, Button
import flashcard as fl
from misc import gp,os


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
    if not IS_ACTIVE: return
    try:
        n = key.__dict__.get('_name_',None)
        global IS_CONTROL,mcon,d3d,MOUSE_POS1,IS_QUES
        #gp(n)
        if n=='ctrl_l':
            IS_CONTROL=True
        if IS_CONTROL:
            match n:
                case 'alt_l':
                    MOUSE_POS1=mcon.position
                case 'cmd':
                    if fl.CARD is not None:
                        x,y = mcon.position
                        if x<MOUSE_POS1[0]:nx,mx=x,MOUSE_POS1[0]
                        else:mx,nx=x,MOUSE_POS1[0]
                        if y<MOUSE_POS1[1]:ny,my=y,MOUSE_POS1[1]
                        else:my,ny=y,MOUSE_POS1[1]
                        bbx=(int(nx),int(ny),int(mx),int(my))
                        img: Image.Image = d3d.screenshot(region=bbx)
                        #img=img.convert('RGB',dither=3,colors=16)
                        #fn = lambda x: 255 if x > 180 else 0
                        fl.CARD._add(img,IS_QUES)
                        #img = img.point(lambda x: 255 if x > 180 else 0, mode='1')
                        gp(f'Added image to {"questions" if IS_QUES else "answers"}')
                    else: gp('No flash card available, image not saved.',2)
                case 'shift':
                    IS_QUES= not IS_QUES
                    gp(f'Toggled {"questions" if IS_QUES else "answers"}')
                case 'up':
                    if len(fl.CARD.ans) != 0 or len(fl.CARD.ques) != 0:
                        ind = fl.save_flcard(fl.CURDR,fl.CARD)
                        fl.CARD=fl.FlashCard()
                        gp(f'Saved flashcard to index: {ind} and moved to next flashcard.')

    except Exception as e:
        gp(e,3)


def key_release(key):
    if not IS_ACTIVE: return
    n = key.__dict__.get('_name_', None)
    global IS_CONTROL
    if n == 'ctrl_l':
        IS_CONTROL=False


# if __name__ == '__main__':
#     itm = 3
#     itm = type(itm)
#     match itm:
#         case 3:
#             gp('int is three')
#         case float():
#             gp('This is a float')
#         case int:
#             gp('this is an int')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
