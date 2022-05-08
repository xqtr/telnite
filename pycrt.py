#!/usr/bin/python3
# -*- coding: CP437 -*-
# coding: CP437

# ------------------------------------------------------------------------
# this file is part of the pycrt project // github.com/xqtr/pycrt 
# ------------------------------------------------------------------------

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

import time
import os, re
import sys
import struct
import tty,termios

#from future import division


cfg_pausestr = '|08[|15Pause|08]'
cfg_popup_box_at = 8
cfg_popup_title_at = 15
cfg_popup_text_at = 7
cfg_popup_pause_at = 8
cfg_popup_pause_str = 'Press any key to continue...|PN'

pathchar = os.sep
pathsep  = os.sep
utf = True

# to change color you can use it like this:  print(colors[7])
# 0 - 15  : foreground colors
# 16 - 31 : background colors

colors = {
 'r':"\033[0m",
  0:"\033[0;30m",
  1:"\033[0;34m",
  2:"\033[0;32m",
  3:"\033[0;36m",
  4:"\033[0;31m",
  5:"\033[0;35m",
  6:"\033[0;33m",
  7:"\033[0;37m",
  8:"\033[1;30m",
  9:"\033[1;34m",
  10:"\033[1;32m",
  11:"\033[1;36m",
  12:"\033[1;31m",
  13:"\033[1;35m",       
  14:"\033[1;33m",
  15:"\033[1;37m",
  16:"\033[40m",
  17:"\033[44m",
  18:"\033[42m",
  19:"\033[46m",
  20:"\033[41m",
  21:"\033[45m",
  22:"\033[43m",      
  23:"\033[47m",
  24:"\033[1;40m",
  25:"\033[1;44m",
  26:"\033[1;42m",
  27:"\033[1;46m",
  28:"\033[1;41m",
  29:"\033[1;45m",
  30:"\033[1;43m",
  31:"\033[1;47m"
}
box_ascii=('.','-','.','|','|','`','-','\'',' ')
# key codes used for the readkey() function below

# common
LF = '\x0d'
CR = '\x0a'
ENTER = '\x0d'
BACKSPACE = '\x7f'
SUPR = ''
SPACE = '\x20'
ESC = '\x1b'

# CTRL
CTRL_A = '\x01'
CTRL_B = '\x02'
CTRL_C = '\x03'
CTRL_D = '\x04'
CTRL_E = '\x05'
CTRL_F = '\x06'
CTRL_G = '\x07'
CTRL_H = '\x08'
CTRL_I = '\x09'
CTRL_J = '\x0a'
CTRL_K = '\x0b'
CTRL_L = '\x0c'

CTRL_N = '\x0e'
CTRL_O = '\x0f'
CTRL_P = '\x10'
"""
q
r
s
t
u
v
w
x
y
"""
CTRL_Y = '\x19'
CTRL_Z = '\x1a'
CTRL_W = ''

# ALT
ALT_A = '\x1b\x61'

# CTRL + ALT
CTRL_ALT_A = '\x1b\x01'

# cursors
UP = '\x1b\x5b\x41'
DOWN = '\x1b\x5b\x42'
LEFT = '\x1b\x5b\x44'
RIGHT = '\x1b\x5b\x43'

CTRL_ALT_SUPR = '\x1b\x5b\x33\x5e'

# other
F1 = '\x1b\x4f\x50'
F2 = '\x1b\x4f\x51'
F3 = '\x1b\x4f\x52'
F4 = '\x1b\x4f\x53'
F5 = '\x1b\x4f\x31\x35\x7e'
F6 = '\x1b\x4f\x31\x37\x7e'
F7 = '\x1b\x4f\x31\x38\x7e'
F8 = '\x1b\x4f\x31\x39\x7e'
F9 = '\x1b\x4f\x32\x30\x7e'
F10 = '\x1b\x4f\x32\x31\x7e'
F11 = '\x1b\x4f\x32\x33\x7e'
F12 = '\x1b\x4f\x32\x34\x7e'

PAGE_UP = '\x1b\x5b\x35\x7e'
PAGE_DOWN = '\x1b\x5b\x36\x7e'
HOME = '\x1b\x5b\x48'
END = '\x1b\x5b\x46'

INSERT = '\x1b\x5b\x32\x7e'
SUPR = '\x1b\x5b\x33\x7e'


KEY_HOME = chr(71)
KEY_UP   = chr(72)
KEY_PGUP = chr(73)
KEY_LEFT = chr(75)
KEY_RIGHT= chr(77)
KEY_END  = chr(79)
KEY_DOWN = chr(80)
KEY_PGDN = chr(81)
KEY_INS  = chr(82)
KEY_DEL  = chr(83)
KEY_BACK = chr(8)
KEY_TAB  = chr(9)
KEY_ENTER= chr(13)
KEY_ESCAPE = chr(27)
KEY_SPACE = chr(32)

KEY_F1 = chr(59)
KEY_F2 = chr(60)
KEY_F3 = chr(61)
KEY_F4 = chr(62)
KEY_F5 = chr(63)
KEY_F6 = chr(64)
KEY_F7 = chr(65)
KEY_F8 = chr(66)
KEY_F9 = chr(67)
KEY_F10 = chr(68)
KEY_F11 = chr(69)
KEY_F12 = chr(70)

KEY_CTRLA  = chr(1) 
KEY_CTRLB  = chr(2) 
KEY_CTRLC  = chr(3) 
KEY_CTRLD  = chr(4) 
KEY_CTRLE  = chr(5) 
KEY_CTRLF  = chr(6) 
KEY_CTRLG  = chr(7) 
KEY_CTRLH  = chr(8) 
KEY_CTRLI  = chr(9) 
KEY_CTRLJ  = chr(10)
KEY_CTRLK  = chr(11)
KEY_CTRLL  = chr(12)
KEY_CTRLM  = chr(13)
KEY_CTRLN  = chr(14)
KEY_CTRLO  = chr(15)
KEY_CTRLP  = chr(16)
KEY_CTRLQ  = chr(17)
KEY_CTRLR  = chr(18)
KEY_CTRLS  = chr(19)
KEY_CTRLT  = chr(20)
KEY_CTRLU  = chr(21)
KEY_CTRLV  = chr(22)
KEY_CTRLW  = chr(23)
KEY_CTRLX  = chr(24)
KEY_CTRLY  = chr(25)
KEY_CTRLZ  = chr(26)

KEY_ALTA  = chr(158)
KEY_ALTB  = chr(176)
KEY_ALTC  = chr(174)
KEY_ALTD  = chr(160)
KEY_ALTE  = chr(146)
KEY_ALTF  = chr(161)
KEY_ALTG  = chr(162)
KEY_ALTH  = chr(163)
KEY_ALTI  = chr(151)
KEY_ALTJ  = chr(164)
KEY_ALTK  = chr(165)
KEY_ALTL  = chr(166)
KEY_ALTM  = chr(178)
KEY_ALTN  = chr(177)
KEY_ALTO  = chr(152)
KEY_ALTP  = chr(153)
KEY_ALTQ  = chr(144)
KEY_ALTR  = chr(147)
KEY_ALTS  = chr(159)
KEY_ALTT  = chr(148)
KEY_ALTU  = chr(150)
KEY_ALTV  = chr(175)
KEY_ALTW  = chr(145)
KEY_ALTX  = chr(173)
KEY_ALTY  = chr(149)
KEY_ALTZ  = chr(172)

NextLine = '\033[{n}E'
PrevLine = '\033[{n}F'
textattr = 7

# screen size variables
rows, columns = os.popen('stty size', 'r').read().split()
screenheight = int(rows)
screenwidth = int(columns)

screenheight = 25
screenwidth = 80

screenbuffer = []
wherex = 1
wherey = 1
savex = -1
savey = -1
utf8=True

def str2hex(s):
  return "".join("{:02x}".format(ord(c)) for c in s)

def init():
  global screenbuffer,screenheight,screenwidth
  rows, columns = os.popen('stty size', 'r').read().split()
  screenheight = int(rows)
  screenwidth = int(columns)
  
  screenheight = 25
  screenwidth = 80
  
  screenbuffer.clear()
  wherex = 1
  wherey = 1
  for y in range(screenheight):
    for x in range(screenwidth):
      screenbuffer.append([' ',7])
      
def stripmci(s):
  i = 0
  val = ''
  inpipe = False
  while i < len(s):
    if len(s) - i > 2:
      if s[i] == '|' and s[i+1].isnumeric() and s[i+2].isnumeric():
        i+=2
      else:
        val += s[i]
    else:
      val += s[i]
    
    i+=1  
  return val
  
def mcilen(st):
  return len(stripmci(st))      
      
def checkxy():
  global wherex,wherey
  global screenwidth,screenheight
  if wherex > screenwidth:
    wherex = 1
    wherey += 1
  if wherey > screenheight:
    wherey = screenheight
      
def getcharat(x,y):
  global screenbuffer,screenheight,screenwidth
  return screenbuffer[(y-1)*screenwidth+(x-1)][0]
    
def getattrat(x,y):
  global screenbuffer,screenheight,screenwidth
  return screenbuffer[(y-1)*screenwidth+(x-1)][1]

def setattrat(x,y,a):
  global screenbuffer,screenheight,screenwidth
  screenbuffer[(y-1)*screenwidth+(x-1)][1] = a
 
# internally used function for wherex/y
def getpos():
    buf = ""
    stdin = sys.stdin.fileno()
    tattr = termios.tcgetattr(stdin)

    try:
        tty.setcbreak(stdin, termios.TCSANOW)
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()

        while True:
            buf += sys.stdin.read(1)
            if buf[-1] == "R":
                break

    finally:
        termios.tcsetattr(stdin, termios.TCSANOW, tattr)

    # reading the actual values, but what if a keystroke appears while reading
    # from stdin? As dirty work around, getpos() returns if this fails: None
    try:
        matches = re.match(r"^\x1b\[(\d*);(\d*)R", buf)
        groups = matches.groups()
    except AttributeError:
        return None

    return (int(groups[0]), int(groups[1]))
    
def savescreen():
  global screenbuffer
  res = list()
  res.extend(screenbuffer)
  return res
  
def savescreen2ansi(filename):
  global screenbuffer,screenheight,screenwidth
  cl = [0,4,2,6,1,5,3,7]
  fg,bg = 7,0
  ofg,obg = 7,0
  olda = 7
  ansi = ''
  CRLF = chr(10)+chr(13)
  
  encode = 'ascii'
  if utf: encode = 'utf-8'
  
  f = open(filename,'w',encoding=encode)
  
  for yy in range(screenheight):
    for xx in range(screenwidth):
      c,a = screenbuffer[xx+(yy*screenwidth)]
      if a!=olda:
        ansi = chr(27)+'['
        fg = a % 16
        bg = a // 16
        if fg>7:
          ansi+='1;'+str(30+cl.index(fg-8))
        else:
          ansi+='0;'+str(30+cl.index(fg))
        ofg = fg
        f.write(ansi+'m')
        ansi = chr(27)+'['
        if bg>7:
          ansi = ''
        else:
          ansi += str(40+cl.index(bg))
        obg = bg
        f.write(ansi+'m')
        olda = a
      f.write(c)
    f.write(CRLF)
    
  
  f.close()

def restorescreen(buff):
  global screenbuffer
  screenbuffer.clear()
  screenbuffer.extend(buff)
  bufflush()
  

# where c can be 0 - 15, changes foreground color
def textcolor(c):
  global textattr
  fg = c % 16
  if fg>15: fg==15
  bg = c // 16
  if bg>15: bg=0
  textattr = c
  sys.stdout.write(colors[fg]+colors[16+bg])
  sys.stdout.flush()
    
# takes a color byte value 0-255 and returns it as an ansi string
# example: textattr2str(31), will give the string for white text in
# blue color    
def textattr2str(a):
    c = a % 16
    d = a // 16
    fg = ''
    bg = ''
    fg = colors[c]
    bg = colors[d+16]
    return fg+bg

# internally used function to spit cp437 chars.    
def swrite(s):    
    #sys.stdout.write(str(s))
    #s="".join(s).encode("CP437")
    os.write(1,bytes(s,"CP437", errors='ignore'))
    #os.write(1,bytes(s,"CP437", errors='surrogateescape'))
    #sys.stdout.write(str(s))
# internally used function to spit cp437 chars.    
def swritexy(x,y,at,s):    
  #sys.stdout.write(str(s))
  #s="".join(s).encode("CP437")
  gotoxy(x,y)
  sys.stdout.write(textattr2str(at))
  sys.stdout.flush()
  os.write(1,bytes(s,"CP437"))
  #sys.stdout.write(str(s))

def bufwritechar(c):
  global screenbuffer,wherex,wherey,textattr
  screenbuffer[(wherey-1)*screenwidth+(wherex-1)][0]=c
  screenbuffer[(wherey-1)*screenwidth+(wherex-1)][1]=textattr
  wherex += 1 
  checkxy()
  
def bufwritestr(s):
  for x in range(len(s)):
    bufwritechar(s[x:x+1])

# writes text, with no new lines, in the current color        
def write(s):
  global wherex,wherey
  if utf:
    #sys.stdout.write(textattr_str)
    sys.stdout.write(str(s))
    sys.stdout.flush()
  else:
    swrite(s)
  bufwritestr(s)
  wherex += len(s)
  checkxy()
  
def screen_write(s):
  if utf:
    #sys.stdout.write(textattr_str)
    sys.stdout.write(str(s))
    sys.stdout.flush()
  else:
    swrite(s)

# same as above but with newline added    
def writeln(st):
  write(st+'\n')

def cursorup(n):
  global wherex,wherey
  sys.stdout.write('\033['+str(n)+'A')
  sys.stdout.flush()
  wherey -= n
  if wherey < 1:
    wherey = 1
    
def cursordown(n):
  global wherex,wherey
  wherey += n
  sys.stdout.write('\033['+str(n)+'B')
  sys.stdout.flush() 
  checkxy()
    
def cursorleft(n):
  global wherex,wherey
  wherex -= n
  sys.stdout.write('\033['+str(n)+'D')
  sys.stdout.flush() 
  if wherex < 1: wherex = 1
    
def cursorright(n):
  global wherex,wherey
  wherex += n
  sys.stdout.write('\033['+str(n)+'C')
  sys.stdout.flush() 
  checkxy()
    
def cursorblock():
  sys.stdout.write('\033[?112c\007')
  sys.stdout.flush() 

def cursorhalfblock():
  sys.stdout.write('\033[?2c\007');
  sys.stdout.flush()

def clrscr():
  sys.stdout.write('\033[2J')
#   n=0 clears from cursor until end of screen,
#   n=1 clears from cursor to beginning of screen
#   n=2 clears entire screen
  sys.stdout.flush()
  init()
  gotoxy(1,1)
   
def clreol():
  sys.stdout.write('\033[2K')
#   n=0 clears from cursor to end of line
#   n=1 clears from cursor to start of line
#   n=2 clears entire line
  sys.stdout.flush()

def ansi_on():
  sys.stdout.write('\033(U\033[0m')
  sys.stdout.flush()

# moves cursor to position i, horizontally
def gotox(i):
  global screenheight,screenwidth
  if x < 1:
    x = 1
  if x > screenwidth:
    x = screewidth
  sys.stdout.write('\033['+str(i)+'G')
  sys.stdout.flush()
  wherex = x

# place cursor at position x,y    
def gotoxy(x,y):
  global screenheight,screenwidth,wherex,wherey
  if x < 1:
    x = 1
  if x > screenwidth:
    x = screenwidth
  if y<1:
    y = 1
  if y>screenheight:
    y=screenheight
  sys.stdout.write('\033['+str(y)+';'+str(x)+'H')
  sys.stdout.flush()
  wherex,wherey = x,y

# writes text at position x,y with color a    
def writexy(x,y,a,s):
  textcolor(a)
  gotoxy(x,y)
  write(s)
  #sys.stdout.write(textattr2str(a))
  #sys.stdout.write(s)
  #sys.stdout.flush()

def writexylist(lst,s):
  writexyw(lst[0],lst[1],lst[2],lst[3],s,lst[4],lst[5])

def writexyw(x,y,a,w,s,char=' ',align='left'):
  gotoxy(x,y)
  textcolor(a)
  if align.upper() == 'LEFT':
    if w>0:
      write(s.ljust(w,char))
    else:
      write(s)
  elif align.upper() == 'RIGHT':
    write(s.rjust(w,char))
  else:
    write(s.center(w,char))
  
def pause(visible=False):
  global cfg_pausestr
  if visible: writepipe(cfg_pausestr)
  ext,key = getkey()
    
def writepipe(txt):
    OldAttr = textattr
    
    width=len(txt)
    Count = 0

    while Count <= len(txt)-1:
        #swrite(str(Count)+' '+str(len(txt))+' '+str(width)
        if txt[Count] == '|':
            Code = txt[Count+1:Count+3]
            try:
                CodeNum = int(Code)
            except:
                CodeNum = -1
                #Count+=1            

            if (Code == '00') or (CodeNum > 0):
                Count = Count +2
                if 0 <= int(CodeNum) < 16:
                    textcolor(int(CodeNum) + ((textattr // 16) * 16))
                else:
                    textcolor((textattr % 16) + (int(CodeNum) - 16) * 16)
            else:
                write(txt[Count:Count+1])
                width = width - 1
      
        else:
            write(txt[Count:Count+1])
            width = width - 1
    

        if width == 0:
            break

        Count +=1
    
    #if width > 1:
    #    write(' '*width)

    
def writexypipe(x,y,attr,width,txt):
    OldAttr = textattr
    OldX    = wherex
    OldY    = wherey

    gotoxy(x,y)
    textcolor(attr)

    Count = 0

    while Count <= len(txt)-1:
        #swrite(str(Count)+' '+str(len(txt))+' '+str(width)
        if txt[Count] == '|':
            Code = txt[Count+1:Count+3]
            CodeNum = int(Code)

            if (Code == '00') or (CodeNum > 0):
                Count = Count +2
                if 0 <= int(CodeNum) < 16:
                    textcolor(int(CodeNum) + ((textattr // 16) * 16))
                else:
                    textcolor((textattr % 16) + (int(CodeNum) - 16) * 16)
            else:
                write(txt[Count:Count+1])
                width = width - 1
      
        else:
            write(txt[Count:Count+1])
            width = width - 1
    

        if width == 0:
            break

        Count +=1
    
    if width > 1:
        write(' '*width)

    textcolor(OldAttr)
    gotoxy(OldX, OldY)
    
    
def setwindow(y1,y2):
  sys.stdout.write('\033[' + str(y1) + ';' + str(y2) + 'r');
  sys.stdout.flush()
    
def resetwindow():
  setwindow(1,25)
    
def cls():
  os.system('cls' if os.name == 'nt' else 'clear')
  init()
  
def delay(t):
  time.sleep(t/ 1000.0)
    
def savecursor():
  global savex,savey,wherex,wherey
  #sys.stdout.write('\033[s')
  savex = wherex
  savey = wherey

def restorecursor():
  global savex,savey,wherex,wherey
  wherex = savex
  wherey = savey
  gotoxy(wherex,wherey)
  savex,savey = -1,-1
  #sys.stdout.write('\033[n')
    
def getcurpos():
  return (getpos()[1],getpos()[0])
    
def ANSIRender(data):
    """
    Return the .ans file data unpacked & in the correct 437 codepage
    """
    #Check terminal width, a width different to 80 normally causes problems
    #rows, cols = os.popen('stty size', 'r').read().split()
    #if cols != "80":
    #    raw_input("\n[!] The width of the terminal is %s rather than 80, this can often cause bad rendering of the .ANS file. Please adjust terminal width to be 80 and press any key to continue....\n"%(cols))

    ans_out = ""
    for a in data:
        ans_out += chr(struct.unpack("B", a)[0]).decode('cp437')

    return ans_out

def dispfile2(filename,wait):
    write(colors[7]+colors[16])
    clrscr()
    with open(filename,encoding="CP437") as fp:  
            lines = fp.readlines()
            cnt = 0
            #write(mci)
            while cnt<=len(lines)-1:
                a=lines[cnt]
                write(a)
                #os.write(1,bytes(a,"CP437"))
                delay(wait)
                cnt+=1    

def dispfile(filename):
    data = open(filename, "rb").read()
    swrite(ANSIRender(data).encode('cp437'))
   
# def readkey():
    # ch1=''
    # ch2=''
    # fd = sys.stdin.fileno()
    # old_settings = termios.tcgetattr(fd)
    # try:
        # tty.setraw(sys.stdin.fileno())
        # ch = sys.stdin.read(1)
    # finally:
        # termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    # return ch
    
fdInput = sys.stdin.fileno()
termAttr = termios.tcgetattr(0)    

# waits user to press a key and returns the value.    
def readkey():
    tty.setraw(fdInput)
    ch = sys.stdin.buffer.raw.read(4).decode(sys.stdin.encoding)
    extended=False
    if len(ch) == 1:
        if ch == ENTER:
            ch = KEY_ENTER
        elif ch == BACKSPACE:
            ch = KEY_BACK
        elif ch == SPACE:
            ch = KEY_SPACE
        elif ch == ESC:
            ch = KEY_ESCAPE
        elif ch == CTRL_A:
            ch = KEY_CTRLA
        elif ch == CTRL_B:
            ch = KEY_CTRLB
        elif ch == CTRL_C:
            ch = KEY_CTRLC
        elif ch == CTRL_D:
            ch = KEY_CTRLD
        elif ch == CTRL_E:
            ch = KEY_CTRLE
        elif ch == CTRL_F:
            ch = KEY_CTRLF
        elif ch == CTRL_G:
            ch = KEY_CTRLG
        elif ch == CTRL_H:
            ch = KEY_CTRLH
        elif ch == CTRL_I:
            ch = KEY_CTRLI
        elif ch == CTRL_J:
            ch = KEY_CTRLJ
        elif ch == CTRL_K:
            ch = KEY_CTRLK
        elif ch == CTRL_L:
            ch = KEY_CTRLL
        elif ch == CTRL_N:
            ch = KEY_CTRLN
        elif ch == CTRL_O:
            ch = KEY_CTRLO
        elif ch == CTRL_P:
            ch = KEY_CTRLP
        elif ch == CTRL_Z:
            ch = KEY_CTRLZ
        elif ch == CTRL_Y:
            ch = KEY_CTRLY
        elif ch == CTRL_W:
            ch = KEY_CTRLW
        elif ord(ch) < 32 or ord(ch) > 126:
            ch = ch
            print(ch)
    else:
        extended = True
        if ch == INSERT:
            ch = KEY_INS
        elif ch == PAGE_DOWN:
            ch = KEY_PGDN
        elif ch == PAGE_UP:
            ch = KEY_PGUP
        elif ch == HOME:
            ch = KEY_HOME
        elif ch == END:
            ch = KEY_END
        elif ch == F1:
            ch = KEY_F1
        elif ch == F2:
            ch = KEY_F2
        elif ch == F3:
            ch = KEY_F3
        elif ch == F4:
            ch = KEY_F4
        elif ch == F5:
            ch = KEY_F5
        elif ch == F6:
            ch = KEY_F6
        elif ch == F7:
            ch = KEY_F7
        elif ch == F8:
            ch = KEY_F8
        elif ch == F9:
            ch = KEY_F9
        elif ch == F10:
            ch = KEY_F10
        elif ch == F11:
            ch = KEY_F11
        elif ch == F12:
            ch = KEY_F12
        elif ord(ch[0]) == 27:
            if ch[1] == "[":
                if ch[2] == "A":
                    ch = KEY_UP
                elif ch[2] == "B":
                    ch = KEY_DOWN
                elif ch[2] == "C":
                    ch = KEY_RIGHT
                elif ch[2] == "D":
                    ch = KEY_LEFT
                elif ch[2] == "K" or ch[2]=="F":
                    ch = KEY_END
                elif ch[2] == "V":
                    ch = KEY_PGUP
                elif ch[2] == "U":
                    ch = KEY_PGDN
    
    termios.tcsetattr(fdInput, termios.TCSADRAIN, termAttr)
    return (ch, extended)
    
def getkey():
    return readkey()

def cleararea(x1,y1,x2,y2,bg):
    for i in range(y2-y1+1):
        gotoxy(x1,y1+i)
        swrite(bg*(x2-x1+1))
        
def byte2str(v):
    s=''.join(str(v))
    return s[2:-1]
    
def bufflush():
  global screenbuffer,screenheight,screenwidth,utf
  global wherex,wherey
  gotoxy(1,1)
  if utf:
    for yy in range(screenheight):
      for xx in range(screenwidth):
        c,a = screenbuffer[xx+(yy*screenwidth)]
        if ord(c)!=0:
          textcolor(a)
          sys.stdout.write(str(c))
          sys.stdout.flush()
  else:
    for yy in range(screenheight):
      for xx in range(screenwidth):
        c,a = screenbuffer[xx+(yy*screenwidth)]
        if ord(c)!=0:
          textcolor(a)
          swrite(c)
  
  wherex = 1
  wherey = 1
 
def ansibox(x1,y1,x2,y2,box=box_ascii):
  gotoxy(x1,y1)
  write(box[0]+box[1]*(x2-x1-1)+box[2])
  gotoxy(x1,y2)
  write(box[5]+box[6]*(x2-x1-1)+box[7])
  for i in range(y2-y1-1):
    gotoxy(x1,y1+1+i)
    write(box[3]+box[8]*(x2-x1-1)+box[4])
    
def popupbox(title,text,y):
  global cfg_popup_title_at, cfg_popup_text_at, cfg_popup_pause_at
  global cfg_popup_pause_str, cfg_popup_box_at
  d = len(text)
  d2 = d // 2
  textcolor(cfg_popup_box_at)
  if d < 25:
    cleararea(26,y,54,y+3," ")
    ansibox(26,y,54,y+3)
  else:
    cleararea(38-d2,y,42+d2,y+3," ")
    ansibox(38-d2,y,42+d2,y+3)
  writexy(38-d2,y,cfg_popup_title_at,title)  
  writexy(40-d2,y+1,cfg_popup_text_at,text)
  writexy(28,y+2,cfg_popup_pause_at,cfg_popup_pause_str)

def charxy(x,y):
  return (getcharat(x,y),getattrat(x,y))

def shadow(x1,y1,x2,y2,attr):
  for i in range(y2-y1):
    writexy(x2+1,y1+1+i,attr,charxy(x2+1,y1+1+i)[0])
  for i in range(x2-x1):
    writexy(x1+2+i,y2+1,attr,charxy(x1+2+i,y2+1)[0])
