#!/usr/bin/python3

import os
import telnetlib
import configparser
import time, datetime
import termios
import atexit
from select import select
import argparse
from pycrt import *
import base64
import ansimg

import pdb

BBSLISTFILE = "https://www.telnetbbsguide.com/bbslist/bbslist.csv"

KBENTER = chr(10)
KBBACK = chr(127)
KBTAB = chr(9)
KBESC = chr(27)
KBCTRLA = chr(1)
KBCTRLW = chr(23)
KBCTRLN = chr(14)
KBBACKSP = chr(8)

ANSICODES = ['A','B','C','D','E','F','G','l','N','O','P','m','n','s','u','J','H','f','h','K']

KBF1 = 'OP'
KBF2 = 'OQ'
KBF3 = 'OR'
KBF4 = 'OS'
KBF5 = '[15'
KBF6 = '[17'
KBF7 = '[18'
KBF8 = '[19'
KBF9 = '[20'
KBF10 = '[21'


KBPAGE_UP = '[5~'
KBPAGE_DOWN = '[6~'
KBHOME = '[H'
KBEND = '[F'
KBINSERT = '[2~'
KBDEL = '[3~'

KBUP = '[A'
KBDOWN = '[B'
KBLEFT = '[D'
KBRIGHT = '[C'

config_input = (12,23,64,255) #x, y, width, maxsize
config_input_gfx_lo = (1,22)
config_input_gfx_hi = config_input_gfx_lo
config_input_attr = 7+16
config_input_fillattr = 1

x,y=1,1
oldxy = [1,1]
WIDTH,HEIGHT=80,25
fattr = 7
mode = 0
CRLF = chr(10)+chr(13)
BEEP=False

APPNAME = "telnite"
CONFIGDIR = os.path.join(os.path.expanduser("~"), ".config")+os.sep+APPNAME+os.sep
CONFIG = configparser.ConfigParser()

QUITEMODE = False
CAPTURE=False
CAPTUREFILE = ''
ENABLEKEYSOUND = False
KBKEYSOUND = ''
KBENTERSOUND = ''
MODEMSOUND = ''

HOST = ""
PORT = 23
BBS = {}
BBS['name'] = ''
BBS['username'] = ''
BBS['password'] = ''
BBS['comment'] = ''
BBS['sysop'] = ''
BBS['software'] = ''
BBS['sounds'] = False
BBS['address'] = ''
BBS['host'] = ''
BBS['www'] = ''
BBS['location'] = ''
BBS['sysop'] = ''

telnet = telnetlib.Telnet()

def readconfigfile():
  global CONFIG,BEEP,WIDTH,HEIGHT,KBBACKSP,ENABLEKEYSOUND,KBKEYSOUND,KBENTERSOUND
  global MODEMSOUND
  
  all_config_files = [CONFIGDIR+APPNAME+'.ini', '/etc/'+APPNAME+'.ini', APPNAME+'.ini']
  CONFIG.read(all_config_files)
  
  BEEP = CONFIG.getboolean("system","beep",fallback=False)
  WIDTH = CONFIG.getint("system","width",fallback=80)
  HEIGHT = CONFIG.getint("system","height",fallback=25)
  KBBACKSP = chr(CONFIG.getint("system","backspace",fallback=8))
  
  ENABLEKEYSOUND = CONFIG.getboolean("sounds","enable",fallback=False)
  KBKEYSOUND = CONFIG.get("sounds","key",fallback='')
  KBENTERSOUND = CONFIG.get("sounds","enter",fallback='')
  MODEMSOUND = CONFIG.get("sounds","modem",fallback='')


def downloadfile(url,filename):
  os.system("wget {} -O {}".format(url,filename))
  
def displayansi(screen):
  if utf:
    print(''.join(str(screen,"cp437")))
  else:
    os.write(1, screen)
    
def bbslistselect(term):
  global HOST,PORT,BBS
  lf = "/tmp/bbslist.csv"
  if not os.path.isfile(lf):
    downloadfile(BBSLISTFILE,lf)
  if not os.path.isfile(lf):
    print("BBS List File not found. Perhaps download failed.")
    return False
  
  csv = open(lf,"r")
  lines = csv.readlines()
  csv.close()
  
  termt = term.upper()
  bbses = []
  
  for line in lines:
    if termt in line.upper():
      bbses.append(line)
  
  if len(bbses)==0:
    print("No matching BBS found.")
    return False
    
  print("Results:")
  print("{:>3}) {:30.30} {:30.30}:{:5}".format('Num','Name','Address','Port'))
  for i,bbs in enumerate(bbses):
    flds=bbs.split(',')
    print("{:>3}) {:30.30} {:30.30}:{:5}".format(i,flds[0],flds[3],flds[4]))
  
  try:
    a= int(input("Select:"))
  except:
    print("Invalid Selection.")
    return False
    
  flds = bbses[a].split(',')
  
  HOST = flds[3]
  if flds[4]!='':
    PORT = flds[4]
  else:
    PORT = 23
    
  BBS['name'] = flds[0]
  BBS['address'] = HOST
  BBS['port'] = PORT
  BBS['sysop'] = flds[1]
  BBS['www'] = flds[5]
  BBS['location'] = flds[6]
  BBS['modem'] = flds[7]
  
  
def approximate_size(size, flag_1024_or_1000=True):
  units = {1000: ['KB', 'MB', 'GB'], 1024: ['KiB', 'MiB', 'GiB']}
  mult = 1024 if flag_1024_or_1000 else 1000
  for unit in units[mult]:
    size = size / mult
    if size < mult:
      return '{0:.3f} {1}'.format(size, unit)

def createconfigfile(path):
  with open(os.path.join(path,APPNAME+".ini"),"w+") as fn:
    fn.write("[system]\n")
    fn.write("beep=0\n")
    fn.write("width=80\n")
    fn.write("height=25\n")
    fn.write("#ASCII key code for use in BACKSPACE press\n")
    fn.write("#8 is Backspace\n")
    fn.write("#127 is Delete\n")
    fn.write("backspace=8\n")
    fn.write("\n")
    fn.write("#Keyboard CLICK sounds\n")
    fn.write("[sounds]\n")
    fn.write("enable=0\n")
    fn.write("#Enter full path and filename to sound file\n")
    fn.write("key=\n")
    fn.write("enter=\n")
    fn.write("modem=\n")
    
  
def clicksound(c):
  global ENABLEKEYSOUND,KBKEYSOUND,KBENTERSOUND

  if ENABLEKEYSOUND==False: return
  
  if c==chr(10):
    os.system("play -q "+KBENTERSOUND+" >> /dev/null 2>&1")
  else:
    os.system("play -q "+KBKEYSOUND+" >> /dev/null 2>&1")

def logopt(s):
  with open('opts.log','a+') as optfile:
    optfile.write(s+"\r\n")

def beep():
  if BEEP:
    os.system("play -n -c1 synth 0.2 sine 500")
    
def renderansi(ansi):
  global x,y,WIDTH,HEIGHT
  global fattr,oldxy,mode
    
  def checkxy():
    global x,y,WIDTH,HEIGHT
    if x>WIDTH:
      x=1
      y+=1
    if y>HEIGHT:
      write(CRLF)
      x=1
      y=HEIGHT
  
  opt = ''
  esc = False
  # matc = [[32 for x in range(h)] for y in range(w)] 
  # matfg = [[7 for x in range(h)] for y in range(w)]
  # matbg = [[7 for x in range(h)] for y in range(w)]
  
  
  ansifg = range(30,38)
  ansibg = range(40,48)
  #ansifgi = [range(90,98)]
  #ansibgi = [range(100,108)]
  pipefg = [0,4,2,6,1,5,3,7]
  
  ansicolor = {30:0, 31:4, 32:2, 33:6, 34:1, 35:5, 36:3, 37:7, 38:0, 39:0, 40:0, 41:64, 42:32, 43:96, 44:16, 45:80, 46:48, 47:112}
  #pipefgh = [8,12,10,14,9,13,11,15]
  #pipebg = [16,20,18,22,17,21,19,23]
  #fgcol = []
  #x=0
  #y=0
  bottom = 0
  
  if len(ansi) == 0:
    return ''
  
  i = 0
  
  s=ansi
  #with open('opts.log','a+') as optfile:
  #            optfile.write(ansi+"\r\n")
  
                
  while i<len(s):
    if not esc:
      if s[i] == chr(27):
        i+=1
        if s[i]!="[":
          esc = False
        else:
          esc = True
      elif s[i] == chr(0):
        pass
      elif s[i] == chr(8): #backspace
        x = max(1,x-1)
        gotoxy(x,y)
      elif s[i] == chr(9):
        #x+=4
        x=min(x+4,WIDTH)
        gotoxy(x,y)
      elif s[i] == chr(7): #BEEP
        x+=1
        checkxy()
        beep()
      elif s[i] == chr(12):
        clrscr()
        x=1
        y=1
      elif s[i]==chr(13):
        x = 1
        checkxy()
        gotoxy(x,y)
      elif s[i]==chr(10):
        x = 1
        y+=1
        checkxy()
        gotoxy(x,y)
      else:
        #pdb.set_trace()
        #print(str(fattr)+"\r\n")
        writexy(x,y,fattr,s[i])
        #logopt("fg:{} - bg:{} - char:{}".format(str(fattr % 16),str(fattr // 16),s[i]))
        esc=False
        x += 1
        checkxy()
    else:
      if s[i] in ANSICODES:
        #esc = False
        #logopt("xODE: "+s[i])
        if s[i] == 'C': #forward
          tx = x
          if opt != '': d = int(opt) 
          else: d =1
          x=min(x+d,WIDTH)
          gotoxy(x,y)
        elif s[i] == 'A': #up
          if opt != '': d = int(opt)
          else: d = 1
          y=max(y-d, 1)
          gotoxy(x,y)
        elif s[i] == 'B': #down
          if opt != '': d = int(opt) 
          else: d =1
          y=min(y+d,HEIGHT)
          gotoxy(x,y)
        elif s[i] == 'D': #back
          if opt != '' : 
            try:
              d = int(opt) 
            except:
              d = 1
          else: 
            d = 1
          x=max(x-d, 1)
          gotoxy(x,y)
        elif s[i] == 'G': # goto to column
          if opt != '': 
            d = int(opt)
            x = d
            gotoxy(x,y)
        elif s[i] == 'h': # terminal codes -> https://man7.org/linux/man-pages/man4/console_codes.4.html
          pass 
        elif s[i] == 'n': #report cursor position
          if len(opt)==0:
            pass
          else:
            d = int(opt)
            if d == 6:
              telnet.write(str(chr(27)+ '[' + str(wherey) + ';' + str(wherex) + 'R').encode("ascii"))
            elif d == 5:
              telnet.write(str(chr(27)+'[0n').encode("ascii")) #terminal ok
              
        elif s[i] == 's': #save cursor
          oldxy = [x,y]
        elif s[i] == 'u': #restore cursor
          x,y = oldxy
        elif s[i] == 'J': #clear entire screen
          if opt == '': opt = '2'
          if int(opt)==2:
            x = 1
            y = 1
            clrscr()
        elif s[i] == 'l': #reset mode? nope
          pass
        elif s[i] == 'K': #clear EOL
          if opt=="": opt="0"
          p = int(opt)
          if p == 2: #erase complete line
            for i in range(1,WIDTH+1):
              writexy(i,y,fattr,' ')
          elif p == 1: #from start to current pos
            for i in range(1,x+1):
              writexy(i,y,fattr,' ')
          elif p == 0 : #from current pos to EOL
            for i in range(x,WIDTH+1):
              writexy(i,y,fattr,' ')
          
        elif s[i] =='H' or s[i] == 'f': #gotoxy
          if len(opt)==0:
            x,y = [1,1]
          else:
            k=opt.split(';')
            if len(k)>2:
              pass
            else:
              y=int(k[0])
              x=int(k[1])
          gotoxy(x,y)
          
        elif s[i]=='m': # set color mode!
          if opt=="":
            fattr = 7
            textcolor(fattr)
          else:
            codes=opt.split(';')
            
            for code in codes:
              num = int(code)
              if num == 0:
                mode = 0
                fattr=7
                textcolor(fattr)
              elif num == 1:
                mode = 1
                fattr = fattr | 0x08
                # fg = fattr % 16
                # bg = fattr // 16
                # if fg<8:fg+=8
                # fattr = fg + (bg*16)
                textcolor(fattr)
              elif num == 5:
                mode = 5
                fattr = fattr | 0x80
                # fg = fattr % 16
                # bg = fattr // 16
                # if fg<8:fg+=8
                # fattr = fg + (bg*16)
                textcolor(fattr)
              elif num == 7:
                fattr = fattr // 16 + ((fattr % 16)*16)
                textcolor(fattr)
              elif num == 8: #conceal
                fg = fattr % 16
                fattr = fg + (fg*16)
                textcolor(fattr)
              elif num in ansifg:
                #fattr = (fattr & 0xF8 + ansicolor[num])
                fg = ansicolor[num]
                bg = fattr // 16
                if mode==1:
                  if fg<8: fg+=8
                fattr = fg + (bg*16)
                textcolor(fattr)
              elif num in ansibg:
                fattr = (fattr % 16 + ansicolor[num])
                textcolor(fattr)
                
              
        opt = ''
        esc=False
      else:
        if s[i] in "0123456789?;": opt += s[i]
    i+=1
 
        
class KBHit():

  def __init__(self):
    # Save the terminal settings
    self.fd = sys.stdin.fileno()
    self.new_term = termios.tcgetattr(self.fd)
    self.old_term = termios.tcgetattr(self.fd)

    # New terminal setting unbuffered
    self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
    termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

    # Support normal-terminal reset at exit
    atexit.register(self.set_normal_term)


  def set_normal_term(self):
    ''' Resets to normal terminal.  On Windows this is a no-op.
    '''
    termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


  def getch(self):
    ''' Returns a keyboard character after kbhit() has been called.
        Should not be called in the same program as getarrow().
    '''
    return sys.stdin.buffer.raw.read(4).decode(sys.stdin.encoding)
    #return sys.stdin.read(3)


  def getarrow(self):
    ''' Returns an arrow-key code after kbhit() has been called. Codes are
    0 : up
    1 : right
    2 : down
    3 : left
    Should not be called in the same program as getch().
    '''
    c = sys.stdin.read(3)[2]
    vals = [65, 67, 66, 68]
    return vals.index(ord(c.decode('utf-8')))

  def kbhit(self):
    dr,dw,de = select([sys.stdin], [], [], 0)
    return dr != []

  def checkkey_nonblock(self):
    global x
    if self.kbhit():
      self.key = self.getch()
      #writexy(1,1,13,"KEY HIT "+self.key)
      
      # print(self.key)
      #for c in self.key:
        #print(ord(c))
      clicksound(self.key)
      if self.key==chr(10):
        telnet.write(b'\r')
      elif self.key==chr(9):
        telnet.write(b'\t')
      #elif self.key==chr(8):
      elif self.key==chr(127):
        #telnet.write(b'\b')
        telnet.write(KBBACKSP.encode("ascii"))
        write(KBBACKSP)
      elif self.key==KBF10 or self.key==KBCTRLW:
        ui.menu()
      else:
        telnet.write(self.key.encode('cp437'))
      
    time.sleep(0.01)
      

class UserInterface:
  # Uses the curses terminal handling library to display a chat log,
  # a list of users in the current channel, and a command prompt for
  # entering messages and application commands.
  badwords = []
  hilites = []
  history = []
  history_index = 0
  
  
  def __init__(self):
    self.inputstring = ''
    self.colors = 16
    self.kb = KBHit()
    
  def savescreen(self):
    print(chr(27)+"[?1049h")
    
  def restorescreen(self):
    print(chr(27)+"[?1049l")
    
  def menu(self):
    self.savescreen()
     
    displayansi(ansimg.BGSCR)
    
    self.kb.getch()
    self.restorescreen()
    
  
  def run(self):
    global QUITEMODE
    totaldatabytes = 0
    logintime = datetime.datetime.now()
    ansibuff=""
    data=""
    buff=""
    while True:
      try:
        data = telnet.read_very_eager().decode('cp437')
      except:
        print("Connection closed...")
        break
      totaldatabytes += len(data)
      if CAPTURE:
        with open(CAPTUREFILE,'a+') as logfile:
          logfile.write(data)
      renderansi(data)
      data=''
     
      try:
        self.kb.checkkey_nonblock()
      except KeyboardInterrupt:
        telnet.close()
        break
    if not QUITEMODE:
      textcolor(7)
      print("")
      print("Total data transfer: {}".format(str(approximate_size(totaldatabytes))))
      print("Connected at: {}".format(logintime.strftime("%Y/%m/%d (y/m/d), %H:%M:%S")))
      print("Stayed connected for: {}".format(str(datetime.datetime.now()-logintime)))
        
def parser():
  global HEIGHT,WIDTH,BEEP,CAPTURE,CAPTUREFILE,QUITEMODE,ENABLEKEYSOUND,KBBACKSP
  global HOST,PORT
  res = True
  parser = argparse.ArgumentParser(description="Telnite // Python3 ANSI-BBS Telnet client for terminal.")
  parser.add_argument('-a','--address', metavar='address[:port]',action='store', type=str, help="The telnet address to connect to.")
  parser.add_argument('-w', '--width', dest='width', action='store', metavar='width', help="Force terminal width in chars.")
  parser.add_argument('--height', dest='height', action='store', metavar='height', help="Force terminal height in chars.")
  parser.add_argument('--telnet-guide', dest='guide', action='store', metavar='term', help="Connect to a BBS from the TelnetBBSGuide.")
  parser.add_argument('-b','--beep', dest='beep', action='store_true', help="Enable BEEP sound, using SOX.")
  parser.add_argument('-d','--del', dest='delete', action='store_true', help="Use #127/DEL code for backspace.")
  parser.add_argument('-c','--capture', dest='capture', action='store_true', help="Store all incoming ANSI data to file.")
  parser.add_argument('--create-config', dest='config', action='store_true', help="Create a default config file (.ini) in current dir.")
  parser.add_argument('-q','--quite', dest='quite', action='store_true', help="Don't display any app. related text")
  parser.add_argument('--no-sound', dest='nosound', action='store_true', help="Disable all sound FXs")
  args = parser.parse_args()
  
  if args.quite:
    QUITEMODE=True
  
  if args.config:
    createconfigfile("./")
    return False
    
  if args.address:
    if ":" in args.address:
      tmp = args.address.split(':')
      HOST = tmp[0]
      PORT = int(tmp[1])
    else:
      HOST = args.address
      PORT = 23
  
  if args.guide:
    bbslistselect(args.guide)
    
  if args.nosound:
    ENABLEKEYSOUND=False
    
  if args.delete:
    KBBACKSP=chr(127)
    
  if args.capture:
    CAPTURE=True
    CAPTUREFILE=time.strftime("capture_%Y%m%dT%H%M%SZ.ans", time.gmtime())
  
  if args.width:
    try:
      WIDTH=int(args.width)
    except:
      WIDTH=80
      
  if args.height:
    try:
      HEIGHT=int(args.height)
    except:
      HEIGHT=80
      
  if args.beep:
    BEEP = True
  
  return res

readconfigfile()
if not parser(): exit()
clrscr()
x,y=1,1
init()
ui = UserInterface()

if ENABLEKEYSOUND:
  os.system("play -q "+MODEMSOUND+" >> /dev/null 2>&1 &")
  
try:
  #telnet = telnetlib.Telnet(HOST,port=PORT,timeout=5)
  if not QUITEMODE: print("Connecting to {}".format(BBS['name']))
  telnet.open(HOST,port=PORT,timeout=5)
  #telnet.set_debuglevel(100)
  time.sleep(1)
except:
  telnet.close()
  exit()
  
ui.run()

telnet.close()








