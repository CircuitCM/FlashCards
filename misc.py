import termcolor

def python_slash(pth: str) -> str:
    chry: [chr] = [ch for ch in pth]
    for i in range(0, len(chry)):
        if chry[i] == '\\':
            chry[i] = '/'
    return ''.join(chry)


def gp(msg, i:int=1):
    clr = 'red'
    if i == 1:
        clr = 'green'
    elif i == 2:
        clr = 'yellow'
    print(termcolor.colored(msg, clr))