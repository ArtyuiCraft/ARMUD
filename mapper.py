from utils import World, Array2D, Array3D
import curses

def main(stdscr):
    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    inclick = False
    while True:
        c = stdscr.getch()
        if c == curses.KEY_MOUSE:
            try:
                event = curses.getmouse()
                x = event[2]
                y = event[1]
                dims = stdscr.getmaxyx()
                stdscr.addstr(0,0,"="*dims[1])
                stdscr.addstr(0,dims[1]-len(str(dims)),str(dims))
                stdscr.addstr(0,0,str(event))
                if event[4] == 4 or inclick or event[4] == 2:
                    stdscr.addstr(x,y,"X")
                    inclick = True
                elif event[4] == 1:
                    inclick = False
            except:
                pass
        stdscr.refresh()

curses.wrapper(main)
