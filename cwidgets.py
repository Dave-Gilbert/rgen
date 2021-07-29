#!/usr/bin/python3

"""

@note

rgen uses curses for screen rendering. 
https://docs.python.org/3/howto/curses.html
"""

import curses
import curses.ascii
from curses import wrapper

stdscr_def = None

def debug(stdscr, arg):
    """
    Print a debugging message at the top of the current window

    @param stdscr: reference to curses output screen, can be None if already initialized
    @param arg: a string based argument

    To initialize call with a non-null value, should be the first thing 
    the program does. Will wait until enter is pressed to proceed in subsequent calls.
    """
    global stdscr_def
    if arg == None and stdscr != None:
        stdscr_def = stdscr
        return
    if stdscr == None:
        stdscr = stdscr_def
    stdscr.addstr(0,10, "DBG> " + str(arg) + "              ")
    stdscr.getch()

def fitItem(item: str, cWidth: int):
    """
    Left justify if item appears to be a number

    @param item: display item in string format
    @param cWidth: width of the cell
    """

    num=True
    for let in item:
        if let.isalpha():
            num = False

    if num:
        item = (" " * cWidth + item + " ")[-cWidth:]
    else:
        item = (" " + item + " " * cWidth)[0:1+cWidth]

    return item


def arrayRowSelect(stdscr, array: list, py: int, px: int, maxpy: int, minw: int, maxw: int, sel: int, nowait: bool) -> int:
    """
    Display a spreadsheet like table, allows selection of row with cursors.

    @param stdscr: ncurses root object
    @param array: 2d array of items to be selected from
    @param py: y position of input widget
    @param px: x position of input widget
    @param maxpy: maximum y position to use, aka bottom of table - 0 to ignore
    @param minw: minimum width of item, 0 to ignore
    @param maxw: maximum width of item, 0 to ignore
    @param sel: the initial selection, 0 == first row
    @param nowait: - just display, don't wait for input

    @return: integer representing selection, 0 .. len(list) - 1
    """

    assert maxpy > py or maxpy == 0
    assert maxw > minw or maxw == 0
    colWidth = []
    twidth = 0
    rows = len(array)
    assert(rows > 0)

    cols = len(array[0])

    maxy, maxx = stdscr.getmaxyx()
    maxy = min(maxy, py + len(array))
    if maxpy > 0:
        maxy = min(maxy, maxpy)

    # Find the maximum rows / cols 

    for col in range(0,cols):
        fwidth = minw
        for row in range(0, rows):
            assert len(array[row]) == cols, str("found array[row]='" + str(array[row]) + "' expected cols = " + str(cols))
            fwidth = max(len(array[row][col])+1, fwidth)
            if maxw > 0:
                fwidth = min(fwidth, maxw)
        colWidth += [fwidth]
        twidth += fwidth + 2

    c = 0
    while True:

        if c == 258:  # down
            sel = sel + 1
        elif c == 259: # up
            sel = sel - 1
        elif c == 339: # pg up
            sel = sel - 5 
        elif c == 338: # pg down
            if sel < len(array) -8:
                sel = sel + 5
            else:
                sel = sel + 1

        elif c == 10: # enter
            return sel

        if sel >= len(array):
            sel = len(array) -1
        elif sel < 0:
            sel = 0

        maxy, maxx = stdscr.getmaxyx()
        if maxpy > 0:
            maxy = min(maxy, maxpy)

        shift = 0
        if py + sel + 5>= maxy:
            shift = (py + sel + 5) - maxy

        # draw all items
        pos = px + 1
        for row in range(shift, min(len(array), maxy - py + shift - 1)):
           pos = px
           for col in range(0, len(colWidth)):
                if  pos + colWidth[col] + 2 < maxx:
                    item = fitItem(array[row][col], colWidth[col])
                    if row == sel and not nowait:
                        stdscr.addstr(py + row - shift, pos, item, curses.A_REVERSE)
                    else:
                        stdscr.addstr(py + row - shift, pos, item)
                else:
                    trim = maxx - pos - 4 
                    if trim > 0:
                        item = fitItem(array[row][col], trim) + " > "
                        stdscr.addstr(py + row - shift, pos, item)

                pos = pos + colWidth[col] + 2

        # debug(stdscr, (row, sel, len(array) - 1, shift))
        # if row + 1 == maxy - py + shift - 1:
        mark = "     "
        if row < len(array) - 1:
            mark = "--V--"
            # if row == maxy - py + shift: 
            # if sel == len(array) - 1:

        for pos in range(0, min(maxx - 5, twidth), 5):
            stdscr.addstr(py + row - shift + 1, pos, mark)

        if nowait:
            stdscr.refresh()            
            return sel

        # reposition cursor
        if py + sel-shift < maxy:
            stdscr.move(py + sel-shift, px)
        stdscr.refresh()
    
        c = stdscr.getch()
 
    

def menuInputH(stdscr, menu :list, py: int, px: int, minw: int, maxw: int, sel: int, nowait: bool) -> int:
    """
    Horizontal menu, with selection.

    @param stdscr: ncurses root object
    @param menu: 1d array of items to be selected from
    @param py: y position of input widget
    @param px: x position of input widget
    @param minw: minimum width of item, 0 to ignore
    @param maxw: maximum width of item, 0 to ignore
    @param sel:   the initial selection, 0 == first item
    @param nowait: if True, just draw the menu and exit

    @return integer representing selection, 0 .. len(list) - 1
    """

    assert(maxw > minw or maxw == 0)
    assert(sel >= 0 and sel < len(menu))

    dmenu = []

    maxy, maxx = stdscr.getmaxyx()
    twidth = 0

    for item in menu:
        fwidth = max(len(item), minw)
        if maxw > 0:
            fwidth = min(fwidth, maxw)

        if twidth + fwidth + 2 + px> maxx:
            break

        dmenu += [(str(item) + " " * maxw)[0:fwidth]]
        twidth += fwidth + 2
    
    c = 0
    while True:

        if c == curses.KEY_RIGHT:
            if sel < len(dmenu) - 1:
                sel = sel + 1
        elif c == curses.KEY_LEFT:
            if sel > 0:
                sel = sel - 1
        elif c == 10: # enter
            return sel



        # draw all items
        pos = px + 1
        s = 0
        for item in dmenu:
            if s == sel:
                stdscr.addstr(py, pos, " " + item + " ", curses.A_REVERSE)
            else:
                stdscr.addstr(py, pos, " " + item + " ")
            pos = pos + len(item) + 2
            s = s + 1

        # reposition cursor
        pos = px + 1
        s = 0
        for item in dmenu:
            if s == sel:
                stdscr.move(py, pos)
                break
            else:
                pass
            pos = pos + len(item) + 2
            s = s + 1

        if nowait:
            return sel
        c = stdscr.getch()
 



 
def displayInp(stdscr, orig :str, py: int, px: int, x: int, ins: bool):
    """
    Display the field for text input.

    @param stdscr ncurses root object
    @param orig original string to be modified
    @param py y position of input widget
    @param px x position of input widget
    @param x x position of cursor

    @return modified string
    """

    maxy, maxx = stdscr.getmaxyx()

    # reprint entire string
    if ins:
        pfix =  ">> "
    else:
        pfix =  ">  "

    shift = 0
    if px + 2 + x + 10 >= maxx:
        shift = (px + 2 + x + 10 ) - maxx

    stdscr.addstr(py, px, pfix + (orig + "<" + " " * (maxx -2))[shift:shift + maxx - px - 3])

    # reposition cursor
    if x == 0:
        stdscr.addstr(py, px + x - shift + 2, ' ')
    else:
        stdscr.addstr(py, px + x - shift + 2, orig[x-1])
    stdscr.refresh()




def input(stdscr, prompt: str, orig :str, py: int, px: int) -> str:
    """
    Wait for user input, supports left, right, home, end, del and bs.

    @param stdscr ncurses root object
    @param prompt prompt followed by "> "
    @param orig original string to be modified
    @param py y position of input widget
    @param px x position of input widget

    @return modified string
    """
    maxy, maxx = stdscr.getmaxyx()
    stdscr.addstr(py,px," " * (maxx - px))
    stdscr.addstr(py,px,prompt)
    px = px + len(prompt)

    x = len(orig)

    ins = True

    c = 0
    while True:

        if c == curses.KEY_RIGHT:
            if x < len(orig):
                x = x + 1
        elif c == curses.KEY_LEFT:
            if x > 0:
                x = x - 1
        elif c == 331: # insert
            if ins:
                ins = False
            else:
                ins = True
        elif c == 330: # del
            if len(orig) == 0:
                pass
            elif x == 0 and len(orig) > 0:
                orig = orig[1:]
            elif x > 0 and x < len(orig):
                orig = orig[0:x] + orig[x+1:]
        elif c == 263: # backspace
            if len(orig) == 0:
                pass
            elif x == 0 and len(orig) > 0:
                orig = orig[1:]
            elif x > 0 and x < len(orig):
                orig = orig[0:x-1] + orig[x:]
                x = x - 1
            elif x == len(orig):
                orig = orig[0:x-1]
                x = x -1                
        elif c == 262: # home
            x = 0
        elif c == 360: # end
            x = len(orig)
        elif curses.ascii.isprint(c):
            if x == len(orig):
                orig += chr(c)
            elif ins == True:
                orig = orig[0:x] + chr(c) + orig[x:]
            else:
                orig = orig[0:x] + chr(c) + orig[x+1:]
            x = x + 1
        elif c == 10: # enter
            return orig
        else:
            stdscr.addstr(0,0, "key = " + str(c))
   
        displayInp(stdscr,  orig, py, px, x, ins)
    
        c = stdscr.getch()
 





                

    












    















    

    



