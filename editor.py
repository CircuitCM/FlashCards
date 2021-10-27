import flashcard as fl
from flashcard import FlashCard
import fastcapture
from misc import gp
from CMDer import command,start_cmdline


CURDR=fl.FLDIR


def go_section(dir:str):
    pass


def new_section(name:str):
    pass


def del_section(all_contents=False):
    pass


def back_section(dir:str):
    pass


def leave_sections():
    pass


def current_section():
    gp(f'Current Section:\n*/{CURDR[fl.FLDIR.rfind("/"):]}')


