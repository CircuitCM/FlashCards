
import sys,io,os
import random as rd
import time

import flashcard as fl
#from flashcard import FlashCard
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtGui import QPixmap, QFont, QCursor, QTextCursor
from PIL.ImageQt import ImageQt
import PIL.Image
from PIL.Image import Image


#gp, walk_all_pickled_files, self_pickled_files,command,try_command=None,None,None,None,None


class App(QWidget):
    UP = 16777235
    DOWN = 16777237
    LEFT = 16777234
    RIGHT = 16777236
    T = 84
    ENTER=16777220

    def __init__(self,size,app):
        super().__init__()
        self.app = app
        x,y=size.width(),size.height()
        x3=x//3
        self.left = x3
        self.top = 30
        self.width = x3
        self.height = y-30-(y//24)
        self.terminal = Terminal(self,self.width, self.height//3)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle('Flash Cards')
        # Create widget
        self.display = QLabel(self)
        self.display.setText('Nothing Loaded.')
        self.display.setWordWrap(True)
        #self.display.setScaledContents(True)
        #pixmap = QPixmap('image.jpeg')
        #self.display.setPixmap(pixmap)
        #self.resize(pixmap.width(), pixmap.height())
        #self.setColor(QPalette.Window, QColor(255, 255, 255))
        self.display.setStyleSheet("background-color: white; border: 1px solid black;")
        self.display.setGeometry(10,10,self.width-20,self.height//2)
        #self.display.setMaximumHeight(self.height//2)
        #self.display.setMaximumWidth(self.width-20)
        self.imwidth =self.width-21
        self.imheight=self.height//2 -1
        self.display.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(24)
        font.setWeight(12)
        self.display.setFont(font)
        self.stats = QLabel(self)
        self.stats.setText('Nothing loaded.')
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setWeight(14)
        self.stats.setFont(font)
        self.stats.setMaximumHeight(20)
        self.layv = QVBoxLayout()
        self.layi=QVBoxLayout()
        self.layi.addWidget(self.display)
        self.layv.addLayout(self.layi)
        self.layv.addWidget(self.stats)
        self.layv.addLayout(self.terminal)
        self.setLayout(self.layv)
        #print(self.children())
        self.seshl: list[str] = []
        self.seshd: list[str] = []
        self.seshp: list[float] = []
        self.sum: float = 1.
        self.addf: float = 1.
        self.multf: float = 2.
        self.divt: float = 1.5

        #mult-div,add-div,elimination
        self.type = 'mult-div'
        self.completions:int = 0
        self.attempts:int = 0
        self.sections:list=[]
        self.is_ques = True
        self.pos=0
        self.set_stats()
        import misc
        misc.gp = self.terminal.cmdResponseShell
        global gp, walk_all_pickled_files, self_pickled_files, command, try_command
        from misc import walk_all_pickled_files as _w, self_pickled_files as _s
        from CMDer import command as _c, try_command as _t
        gp, walk_all_pickled_files, self_pickled_files, command, try_command = self.terminal.cmdResponseShell, _w, _s, _c, _t
        command(['show','section'])(self.show_section)
        command(['go','section'],(str,),1,1)(self.go_section)
        command(['back','section'])(self.back_section)
        command(['leave', 'sections'])(self.leave_sections)
        command(['restart', 'session'])(self.restart_session)
        command(['change', 'session'],(str,),1,1)(self.restart_session)
        command(['addition'],(float,),1,1)
        command(['multiple'], (float,), 1, 1)
        command(['divisor'], (float,), 1, 1)
        command(['new', 'session'], (str,str), 1, 2)(self.new_session)
        command(['font','size'],(int,),1,1)(self.set_font)
        self.show()

    def set_stats(self):
        #'{:.1%}'.format(1/3.0)
        self.stats.setText(f'{" ".join(self.sections)},  type: {self.type}{((", multiple: "+str(self.multf) if self.type=="mult-div" else ", addition: "+str(self.addf))+", divisor: "+str(self.divt)) if self.type!="elimination" else ""},  efficacy: {self.completions}/{self.attempts},  {"{:.1%}".format(self.completions/self.attempts if self.attempts!=0 else 0)}')

    # key press events dont work when terminal is in use (or when returning to window focus wierd bug)
    def keyPressEvent(self,event):
        #inp = self.terminal.input
        k=event.key()
        match k:
            case App.ENTER:
                if not self.terminal.input.hasFocus():
                    self.terminal.input.setFocus()
                elif self.terminal.prevtx is None:
                    self.setFocus()
            case App.T:
                self.toggle_quesans()
            case App.UP:
                self.display_to(1)
            case App.DOWN:
                self.display_to(-1)
            case App.LEFT:
                self.missed_fl()
            case App.RIGHT:
                self.done_fl()


    # def keyReleaseEvent(self, event):
    #     k = event.key()
    #     return
    #     if self.TKEYS[k]:
    #         self.keyholds[k] = False

    def show_section(self):
        gp(f'In Section:\n*/{fl.CURDR[len(fl.CDIR):]}')

    def go_section(self,name: str, check=True):
        if check:
            if name[-1] != '/': name = name + '/'
            if not os.path.isdir(f"{fl.CURDR}{name}"):
                gp("This section doesn't exist.", 3)
                return
        fl.CURDR = f"{fl.CURDR}{name}"
        self.show_section()

    def back_section(self):
        fl.CURDR = fl.CURDR[:fl.CURDR.rfind('/') + 1]
        self.show_section()

    def leave_sections(self):
        fl.CURDR = fl.FLDIR
        self.show_section()

    def clear_session(self):
        self.seshl.clear()
        self.seshd.clear()
        self.seshp.clear()
        self.sum:float = 1.
        self.addf:float = 1.
        self.multf:float = 2.
        self.divt:float = 1.5

        # mult-div,add-div,elimination
        self.type = 'mult-div'
        self.completions = 0
        self.attempts = 0
        self.is_ques = True
        self.pos=0
        gp('Session cleared.')

    def set_add(self,ad:float):
        if ad<=0:gp('Additive penalty must be greater than 0.',3)
        else:
            self.addf=ad
            gp(f'Additive penalty set to {ad}', 1)

    def set_mult(self,mult:float):
        if mult<=1:gp('Multiplicative penalty must be greater than 1.',3)
        else:
            self.multf=mult
            gp(f'Multiplicative penalty set to {mult}', 1)

    def set_div(self,div:float):
        if div<=1:gp('Divisible subsidy must be greater than 1.',3)
        else:
            self.divt=div
            gp(f'Divisible subsidy set to {div}', 1)

    def restart_session(self):
        match self.type:
            case 'mult-div' | 'add-div':
                for i in range(0,len(self.seshp)): self.seshp[i]=1
                self.sum=len(self.seshp)
            case 'elimination':
                self.seshl.extend(self.seshd)
                self.seshd.clear()
        self.completions = 0
        self.attempts = 0
        self.is_ques = True
        self.set_stats()
        gp('Restarted current session.')

    def change_session(self,ntype:str):
        ntype=ntype.lower()
        match ntype,self.type:
            case (self.type,_):
                gp(f'Already a {ntype} session.',2)
            case ('elimination'|'mult-div'|'add-div', 'mult-div'|'add-div'):
                gp(f'Switched session type from {self.type} to {ntype}')
                self.type = ntype
                self.set_stats()
            case ('mult-div'|'add-div', _):
                gp(f'Switched session type from {self.type} to {ntype}')
                self.type = ntype
                self.seshl.extend(self.seshd)
                self.seshp=[1 for _ in range(0,len(self.seshl))]
                self.sum=len(self.seshp)
                gp('Warning: elimination to continuous resets probabilities',2)
                self.set_stats()
            case (_,_):
                gp(f'Unkown session type',3)

    def new_session(self,type:str,sects:str='all'):
        if type.lower()not in {'mult-div','add-div','elimination'}:
            gp('Unkown session type.',2)
            return
        select = {*filter(lambda x: x!=''or x!=' ',sects.lower().split(','))}
        nl = []
        dses = [fl.CURDR[fl.CURDR.rfind('/')+1:]+':',]
        if 'all' in select:
            walk_all_pickled_files(nl,fl.CURDR)
            dses.append('all')
        else:
            if 'self' in select:
                select.remove('self')
                self_pickled_files(nl,fl.CURDR)
                dses.append('self')
            for i in select:
                walk_all_pickled_files(nl,fl.CURDR+i)
                dses.append(i)
        if len(nl)==0:
            gp('No cards found, no new session made.',2)
        else:
            self.clear_session()
            match type.lower():
                case 'mult-div' | 'add-div':
                    self.seshp = [1 for _ in range(0, len(nl))]
                    self.sum=len(self.seshp)
                    self.seshl = nl
                    self.type=type.lower()
                case 'elimination':
                    self.seshl = nl
                    self.type='elimination'
                case _:
                    gp('Unkown session type.',2)
            self.sections = dses
            fl.CARD = self.load_random_fl()
            self.is_ques = True
            self.display_to()
            self.set_stats()
            gp('New session created.')

    def set_font(self,fontsize:int):
        fnt = self.display.font()
        fnt.setPointSize(fontsize)
        self.display.setFont(fnt)

    def toggle_quesans(self):
        self.is_ques = not self.is_ques
        self.display_to()
        gp(f'Toggled {"questions" if self.is_ques else "answers"}')

    def done_fl(self):
        if len(self.seshl)==0:
            gp('Session is already finished.', 2)
            return
        self.attempts += 1
        self.completions += 1
        self.next_flcard(False)
        self.set_stats()
        gp('Flashcard completed.', 1)

    def missed_fl(self):
        if len(self.seshl)==0:
            gp('Session is already finished.', 2)
            return
        self.attempts += 1
        #self.completions += 0
        self.next_flcard()
        self.set_stats()
        gp('Flashcard missed.',2)

    def get_fl_card_item(self,pos: int = 0):
        #if fl.CARD is None: return None shouldnt happen
        if self.is_ques:
            psit = fl.CARD.pques + pos
            if len(fl.CARD.ques)> psit >= 0:
                fl.CARD.pques = psit
                return fl.CARD.ques[psit]
            else:
                return None
        else:
            psit = fl.CARD.pans + pos
            if len(fl.CARD.ans) > psit >= 0:
                fl.CARD.pans = psit
                return fl.CARD.ans[psit]
            else:
                return None

    def load_random_fl(self):
        match self.type:
            case 'elimination':
                self.pos = rd.randrange(0, len(self.seshl))
            case 'add-div'|'mult-div':
                ps = rd.uniform(0,self.sum)
                for i in range(0,len(self.seshp)):
                    ps-=self.seshp[i]
                    if ps<=0:
                        self.pos=i
                        break
        self.setWindowTitle(self.seshl[self.pos][len(fl.CDIR):])
        return fl.load_flcard(self.seshl[self.pos])

    def next_flcard(self,missed=True):
        if missed:
            match self.type:
                case 'add-div':
                    self.seshp[self.pos]+=self.addf
                    self.sum = sum(self.seshp)
                case 'mult-div':
                    #nq=self.multf*self.seshp[self.pos]
                    #self.sum += nq-self.seshp[self.pos] otherwise rounding errors add up
                    self.seshp[self.pos] = self.multf*self.seshp[self.pos]
                    self.sum = sum(self.seshp)
        else:
            match self.type:
                case 'elimination':
                    self.seshd.append(self.seshl.pop(self.pos))
                    if len(self.seshl)==0:
                        gp('Elimination session finished!')
                        return
                case 'add-div' | 'mult-div':
                    self.seshp[self.pos] = self.seshp[self.pos]/self.divt
                    self.sum=sum(self.seshp)

        #flashcards dont get saved so loading new ones pques and pans goes to zero
        fl.CARD = self.load_random_fl()
        self.is_ques=True
        self.display_to()

    def display_to(self,move:int=0):
        itm = self.get_fl_card_item(move)
        match itm:
            case None:
                gp('No more items or no flashcard loaded.',2)
            case str():
                self.put_txt(itm)
            case io.BytesIO():
                self.put_img(itm)

    def put_img(self,imbyts:io.BytesIO):
        xy = self.display.size()
        self.display.clear()
        w, h = xy.width(), xy.height()
        pm=QPixmap.fromImage(ImageQt(PIL.Image.open(imbyts)).copy())
        x, y = pm.width(), pm.height()
        r = (y / x) * (w / h)
        if r < 1.0:
            nh = int(h * r)
            nw = w
        else:
            nh = h
            nw = int(w / r)
        dw = (x - nw) // 2
        dh = (y - nh) // 2
        pm = pm.scaled(nw,nh,transformMode=Qt.SmoothTransformation)
        self.display.setContentsMargins(dw, dh, dw, dh)
        self.display.setPixmap(pm)

    def put_txt(self,txt:str):
        self.display.clear()
        self.display.setText(txt)



CTXT = {0:"<span style=\" font-weight:500; color:#000000;\" >",
            1:"<span style=\" font-weight:600; color:#00aa00;\" >",
            2:"<span style=\" font-weight:600; color:#daa520;\" >",
            3:"<span style=\" font-weight:600; color:#ff0000;\" >"}
SPAN = "</span>"


class Terminal(QVBoxLayout):

    def __init__(self,pwid:QWidget,width=0,height=0):
        super(Terminal, self).__init__()
        self.cmd = QTextEdit(pwid)
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.cmd.setFont(font)
        self.cmd.viewport().setProperty("cursor", QCursor(Qt.IBeamCursor))
        self.cmd.setMaximumHeight(height)
        self.cmd.setMinimumHeight(height)
        #self.cmd.setMaximumWidth(300)
        self.cmd.setReadOnly(True)
        self.addWidget(self.cmd)
        self.input = QLineEdit(pwid)
        self.input.setFont(font)
        #self.input.setMaximumWidth(300)
        #self.input.setMinimumWidth(300)
        self.addWidget(self.input)

        # self.lineEdit.textEdited['QString'].connect(self.textEdit.setMarkdown)
        self.input.returnPressed.connect(self.inputCmd)
        self.prevtx = None

    def echoTxt(self):
        txt = self.input.text() + "\n"
        self.input.clear()
        self.cmd.insertPlainText(txt)
        vbar = self.cmd.verticalScrollBar()
        vbar.setValue(vbar.maximum() - 13)

    def cmdResponseShell(self, txt,num=1):
        if type(txt) is not str: txt=str(txt)
        if txt in {'',' '}:return
        vbar = self.cmd.verticalScrollBar()
        vbar.setValue(vbar.maximum() - 13)
        txtc=self.cmd.textCursor()
        txtc.movePosition(QTextCursor.End,QTextCursor.MoveAnchor,1)
        self.cmd.setTextCursor(txtc)
        if '\n' in txt:
            tls = txt.split('\n')
            for w in tls:
                self.cmd.insertHtml(CTXT[num] + w + SPAN)
                self.cmd.insertPlainText('\n')
        else:
            self.cmd.insertHtml(CTXT[num] + txt + SPAN)
            self.cmd.insertPlainText('\n')
        if num==0:self.prevtx=txt


    def inputCmd(self):
        tx= self.input.text()
        self.prevtx=tx
        if tx!= '':
            txt = tx + "\n"
            self.input.clear()
            self.cmd.insertHtml(CTXT[0]+txt+SPAN)
            self.cmd.insertPlainText('\n')
            vbar = self.cmd.verticalScrollBar()
            vbar.setValue(vbar.maximum() - 13)
            try_command(tx)
        else:
            self.prevtx = None


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


if __name__ == '__main__':
    #print('launched')
    app = QApplication(sys.argv)
    scrn = app.primaryScreen()
    # print(scrn.name())
    # sz=scrn.size()
    # print(f'{sz.width()},{sz.height()}')
    # rect = scrn.availableGeometry()
    # print(f'{rect.width()},{rect.height()}')
    ex = App(scrn.availableGeometry(),app)
    sys.exit(app.exec_())