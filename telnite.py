#!/usr/bin/python3

import os
import telnetlib
import configparser
import textwrap
import time, datetime
import termios
import atexit
from select import select
import argparse
from pycrt import *
import base64
import ansimg
import re

import pdb

BBSLISTFILE = "https://www.telnetbbsguide.com/bbslist/bbslist.csv"

ZMODEMSTR = ""

KBENTER = chr(10)
KBBACK = chr(127)
KBTAB = chr(9)
KBESC = chr(27)
KBCTRLA = chr(1)
KBCTRLW = chr(23)
KBCTRLN = chr(14)
KBCTRLL = chr(12)
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

KBUP = chr(27)+'[A'
KBDOWN = chr(27)+'[B'
KBLEFT = chr(27)+'[D'
KBRIGHT = chr(27)+'[C'

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

opt = ''
esc = False

APPNAME = "telnite"
CONFIGDIR = os.path.join(os.path.expanduser("~"), ".config")+os.sep+APPNAME+os.sep
TMPDIR = '/tmp/'
CONFIG = configparser.ConfigParser(interpolation=None)


QUITEMODE = False
CAPTURE=False
CAPTUREFILE = ''
ENABLEKEYSOUND = False
KBKEYSOUND = ''
KBENTERSOUND = ''
MODEMSOUND = ''
STATUSBAR = '30'

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
BBS['index'] = ''

REGEX = []
TEXT = ""

program_descripton = f'''
    Telnite v1.0
    -------------
    
    An ANSI-BBS telnet client for use in terminals like Gnome_terminal, xterm, etc.

    Created by XQTR of Another Droid BBS 
    
    [] https://github.com/xqtr/telnite
    [] telnet://andr01d.zapto.org:9999
    
    Licensed under GPL3
   
    '''
    
cs_numbers = " 1234567890"
cs_phone = " 1234567890#+-/"
cs_upper = " QWERTYUIOPASDFGHJKLZXCVBNM"
cs_lower = " qwertyuiopasdfghjklzxcvbnm"
cs_symbols = " ~-=!@#$%^&*()_+[]}{;:'\"\|,<.>/?"
cs_printable = cs_lower+cs_upper+cs_symbols+cs_numbers
cs_email = cs_numbers+cs_lower+cs_upper+"@."
cs_email = cs_email.replace(" ", "")
cs_www = cs_numbers+cs_upper+cs_lower+"/-.:"

telnet = telnetlib.Telnet()

def istermux():
  global CONFIGDIR,TMPDIR
  CONFIGDIR = os.path.join(os.path.expanduser("~"), ".config")+os.sep+APPNAME+os.sep
  s = os.path.expanduser("~")
  if "com.termux" in s:
    TMPDIR = '/data/data/com.termux/files/usr/tmp/'
  else:
    TMPDIR = '/tmp/'

class RawFormatter(argparse.HelpFormatter):
  def _fill_text(self, text, width, indent):
    return "\n".join([textwrap.fill(line, width) for line in textwrap.indent(textwrap.dedent(text), indent).splitlines()])

def statusbar(s):
  global WIDTH,HEIGHT,STATUSBAR
  writexy(1,HEIGHT,int(STATUSBAR),s.ljust(WIDTH))

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")
  
def initoBBS(filename):
  global BBS
  parser = configparser.ConfigParser()
  parser.read(filename)
  
  for option in parser.options("BBS-Info"):
    BBS[option] = parser.get("BBS-Info", option)
  BBS['sounds'] = str2bool(BBS['sounds'])
  

def readconfigfile():
  global CONFIG,BEEP,WIDTH,HEIGHT,KBBACKSP,ENABLEKEYSOUND,KBKEYSOUND,KBENTERSOUND
  global MODEMSOUND,STATUSBAR,REGEX
  
  if not os.path.isdir(CONFIGDIR):
    os.makedirs(CONFIGDIR)
  
  all_config_files = [CONFIGDIR+APPNAME+'.ini', '/etc/'+APPNAME+'.ini', APPNAME+'.ini']
  CONFIG.read(all_config_files)
  
  BEEP = CONFIG.getboolean("system","beep",fallback=False)
  WIDTH = CONFIG.getint("system","width",fallback=80)
  HEIGHT = CONFIG.getint("system","height",fallback=25)
  KBBACKSP = chr(CONFIG.getint("system","backspace",fallback=8))
  STATUSBAR =  CONFIG.get("system","statusbar",fallback='30')
  
  ENABLEKEYSOUND = CONFIG.getboolean("sounds","enable",fallback=False)
  KBKEYSOUND = CONFIG.get("sounds","key",fallback='')
  KBENTERSOUND = CONFIG.get("sounds","enter",fallback='')
  MODEMSOUND = CONFIG.get("sounds","modem",fallback='')

  ind=1
  while True:
    if CONFIG.has_section("regex_"+str(ind)):
      section = "regex_"+str(ind)
      rx = {}
      rx['name'] = CONFIG.get(section,'name')
      rx['regex'] = CONFIG.get(section,'regex')
      rx['cmd'] = CONFIG.get(section,'command')
      REGEX.append(rx)
      ind+=1
    else:
      break  

def downloadfile(url,filename):
  os.system("wget {} -O {}".format(url,filename))
  
def displayansi(screen):
  if utf:
    print(''.join(str(screen,"cp437")))
  else:
    os.write(1, screen)
    
def bbslistselect(term):
  global HOST,PORT,BBS
  files = [f for f in os.listdir(CONFIGDIR) if f!=APPNAME+'.ini' and term.lower() in f.lower()]
  if len(files)==0:
    print("No matching BBSes!")
    return False
   
  print("Results:")
  print("{:>3}) {:30.30}".format('Num','Address'))
  for i,f in enumerate(files):
    print("{:>3}) {:30.30}".format(i,f[:-4]))
    
  try:
    a= int(input("Select:"))
  except:
    print("Invalid Selection.")
    return False
    
  #print(files[a])
  initoBBS(CONFIGDIR + files[a])
  
  HOST = BBS['address'].split(':')[0]
  PORT = BBS['address'].split(':')[1]
  return True
  
def bbstglistselect(term):
  global HOST,PORT,BBS,TMPDIR
  lf = TMPDIR + "bbslist.csv"
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
  BBS['sysop'] = flds[1]
  BBS['www'] = flds[6]
  BBS['location'] = flds[7]
  BBS['modem'] = flds[8]
  return True

def togglecapture():
  global CAPTURE,CAPTUREFILE
  CAPTURE=not CAPTURE
  if CAPTURE:
    CAPTUREFILE=time.strftime("capture_%Y%m%dT%H%M%SZ.ans", time.gmtime())
  return CAPTURE
  
def getfilename():
  global HOST
  ind = 0
  while True:
    if not os.path.isfile(HOST+'_'+str(ind).zfill(5)+'.ans'):
      return HOST+'_'+str(ind).zfill(5)+'.ans'
      break
    else:
      ind+=1
  
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
    fn.write("statusbar=30\n")
    fn.write("\n")
    fn.write("#Keyboard CLICK sounds\n")
    fn.write("[sounds]\n")
    fn.write("enable=0\n")
    fn.write("#Enter full path and filename to sound file\n")
    fn.write("key=\n")
    fn.write("enter=\n")
    fn.write("modem=\n")
    fn.write("\n")
    fn.write("[regex_1]")
    fn.write("Name=Email")
    fn.write("RegEx=[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,6}")
    fn.write("Command=")
    fn.write("\n")
    fn.write("[regex_2]")
    fn.write("Name=Date")
    fn.write("RegEx=\d{1,2}[-_/]\d{1,2}[-_/]\d{4}")
    fn.write("Command=")
    fn.write("\n")
    fn.write("[regex_3]")
    fn.write("Name=BBS Node Address")
    fn.write("RegEx=\d{1,3}:\d{1,4}\/\d{1,3}")
    fn.write("Command=%P/nodefinder/node.py '%M'")
    fn.write("\n")
    fn.write("[regex_4]")
    fn.write("Name=URL/HTTP")
    fn.write("RegEx=https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")
    fn.write("Command=firefox %M")
    fn.write("\n")
    fn.write("[regex_5]")
    fn.write("Name=URL/Gopher")
    fn.write("RegEx=gopher:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")
    fn.write("Command=lynx %M")
    fn.write("\n")
    fn.write("[regex_6]")
    fn.write("Name=Magnet Link")
    fn.write("RegEx=magnet:\?xt=urn:(btih:)?[A-Za-z0-9]{32,42}")
    fn.write("Command=transmission-gtk %M")
    fn.write("\n")
    fn.write("[regex_7]")
    fn.write("Name=ZIP Code")
    fn.write("RegEx=[0-9]\{5\}(-[0-9]\{4\})?")
    fn.write("Command=")
  
  print("")
  print("Config file created at path:")
  print(path)
  print("If this is the current folder you are in, consider moving it, at")
  print("the system config path, which is:")
  print(CONFIGDIR)
  print("All other config/app related files are saved there also.")
  print("")

def findregex():
  global screenbuffer,screenheight,screenwidth,REGEX,TEXT
  found = False
  results = []
  ui.savescreen()
  ix,iy = 3,3
  a = textattr
  textcolor(7)
  clrscr()
  writexy(1,1,7,"Results:")
  writexy(1,2,7,"{:2} {:15} {:50}".format('##','Type','Result'))
    
  i=0
  for rx in REGEX: 
    res = re.findall(rx['regex'], TEXT)
    if res:
      #print("M>>>"+m.group())
      found = True
      for r in res: 
        writexy(1,iy,7,"{:2} {:15} {:50}".format(str(i),rx['name'],str(r)))
        i+=1
        s = rx['cmd']
        s = s.replace('%M',str(r))
        results.append(s)
        iy+=1
   
  if not found:
    writexy(1,4,7,'No RegEx matches found... Press key to continue.')
    ui.kb.readkey()
  else:
    print("")
    try:
      a= int(input("Enter selection:"))
      os.system(results[int(a)])
    except:
      print("Invalid Selection.")
    
    
    

  ui.restorescreen()
  textcolor(a)
      
  
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
  global x,y,WIDTH,HEIGHT,TEXT,ZMODEMSTR
  global fattr,oldxy,mode,esc,opt
    
  def checkxy():
    global x,y,WIDTH,HEIGHT
    if x>WIDTH:
      x=1
      y+=1
    if y>HEIGHT:
      write(CRLF)
      x=1
      y=HEIGHT
  
  
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
    #print(i,len(s))
    if not esc:
      if s[i] == chr(27):
        esc = True
        # i+=1
        # if s[i]!="[":
          # esc = False
        # else:
          # esc = True
      elif s[i] == chr(0):
        pass
      elif s[i] == chr(24): #zmodem?
        if len(s)-i>3:
          zstr = s[i+1:i+5]
          if zstr.strip() == 'B000': #download
            os.system(ZMODEMSTR)
          elif zstr.strip() == 'B001': #upload
            pass
        else:  #not enough chars to check if it's a zmodem request
          writexy(x,y,fattr,s[i])
          TEXT += s[i]
          esc=False
          x += 1
          checkxy()
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
        TEXT = ''
        x=1
        y=1
      elif s[i]==chr(14):
        write('X')
      elif s[i]==chr(15):
        write('X')
      elif s[i]==chr(13):
        x = 1
        checkxy()
        gotoxy(x,y)
      elif s[i]==chr(10):
        #x = 1
        y+=1
        checkxy()
        gotoxy(x,y)
      else:
        #pdb.set_trace()
        #print(str(fattr)+"\r\n")
        writexy(x,y,fattr,s[i])
        TEXT += s[i]
        #logopt("fg:{} - bg:{} - char:{}".format(str(fattr % 16),str(fattr // 16),s[i]))
        esc=False
        x += 1
        checkxy()
    else:
      if s[i] == '[':
        pass
      elif s[i] in ANSICODES:
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
          write(chr(27)+'['+opt+'h')
        elif s[i] == 'l': 
          write(chr(27)+'['+opt+'l')
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
            TEXT = ''
        elif s[i] == 'l': #reset mode? nope
          pass
        elif s[i] == 'K': #clear EOL
#          pdb.set_trace()
          if opt=="": opt="0"
          p = int(opt)
          if p == 2: #erase complete line
            for d in range(1,WIDTH+1):
              writexy(d,y,fattr,' ')
          elif p == 1: #from start to current pos
            for d in range(1,x+1):
              writexy(d,y,fattr,' ')
          elif p == 0 : #from current pos to EOL
            for d in range(x,WIDTH+1):
              writexy(d,y,fattr,' ')
        elif s[i] =='H' or s[i] == 'f': #gotoxy
          if len(opt)==0:
            x,y = [1,1]
          else:
            k=opt.split(';')
            if len(k)>2:
              pass
            elif len(k)==2:
              y=int(k[0])
              x=int(k[1])
              gotoxy(x,y)
            else:
              pass
          
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
                textcolor(fattr)
              elif num == 5:
                mode = 5
                fattr = fattr | 0x80
                textcolor(fattr)
              elif num == 7:
                fattr = fattr // 16 + ((fattr % 16)*16)
                textcolor(fattr)
              elif num == 8: #conceal
                fg = fattr % 16
                fattr = fg + (fg*16)
                textcolor(fattr)
              elif num in ansifg:
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
    
  def readkey(self):
    return self.getch()


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
    global x,BBS
    if self.kbhit():
      self.key = self.getch()
      #writexy(1,1,13,"KEY HIT "+self.key)
      
      # print(self.key)
      #for c in self.key:
        #print(ord(c))
      clicksound(self.key)
      if self.key==chr(10):
        telnet.write(b'\r')
      elif self.key==chr(12): #CTRL-L
        telnet.write(BBS['username'].encode('cp437'))
        telnet.write(b'\r')
        telnet.write(BBS['password'].encode('cp437'))
        telnet.write(b'\r')
      elif self.key==chr(18): #CTRL-R find regex
        findregex()
      elif self.key==chr(1): #CTRL-A Save screen
        fn = getfilename()
        savescreen2ansi(fn)
        statusbar('Screen saved in: '+fn)
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
        
      
    #time.sleep(0.01)
      

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
    self.logintime = 0
    self.totaldatabytes = 0
    
  def getyesno(self,x,y,trueat,falseat,offat,default):
    """
    Function to get a Yes/No answer
    trueat  : color in byte value for the No button
    falseat : color in byte value for the Yes button
    default : True/False to begin with 
    """
    key = ""
    val = {0:'No ',1:'Yes'}
    res = default
    while key != KBENTER:
        writexy(x,y,offat,val[True]+val[False])
        if res == True:
            writexy(x,y,trueat,val[res])
        else:
            writexy(x+3,y,falseat,val[res])
        gotoxy(1,25)
        key = self.kb.readkey()
        if key == KBLEFT or key == KBRIGHT or key == " ":
            res = not res
        elif key == KBESC:
            return None
            break
    #return val[res].lower().strip(" ")
    return res
    
  def xinput(self,x,y,att,fillatt,chars,length,maxc,fc,default):
    """
    Simple function to get an input from user
    att    : fg color
    fillatt: bg color
    chars  : string with valid characters.
    length : length for the input box
    maxc   : maximum size for the string to be entered
    fc     : fill character for the bg
    default: default value
    """
    pos = 0
    res = default
    key = ""
    while key != KBENTER:
        writexy(x,y,fillatt,fc*length)
        writexy(x,y,att,res[pos:length+pos])
        gotoxy(x+len(res[pos:length+pos]),y)
        key = self.kb.readkey()
        
        if key in chars:
            res = res + key
            if len(res)>length:
                if len(res)<maxc:
                    pos += 1
        elif key == " ":
            res = res + " "
            if len(res)>length:
                if len(res)<maxc:
                    pos += 1
        elif key == KBBACK:
            res = res[:-1]
            pos = pos - 1
            if pos < 0:
                pos = 0
        elif key == KBCTRLA:
            res = ""
        elif key == KBENTER:
            break
        elif key == KBESC:
            res = "-1"
            break
    writexy(x,y,fillatt,fc*length)
    writexy(x,y,fillatt,res[:length])
    return res
    
  def savescreen(self):
    print(chr(27)+"[?1049h")
    
  def restorescreen(self):
    print(chr(27)+"[?1049l")
    
  def savebbsmenu(self):
    global BBS,HOST,PORT
    clrscr()
    displayansi(ansimg.BGSCR)
    xx,yy = 17,10
    dd = 16
    aa = 15+16*3
    
    while True:
      writexy(xx,yy,7,"Enter BBS Name:")
      a = self.xinput(xx+dd,yy,aa,aa,cs_printable,35,35,' ',BBS['name'])
      if a!="-1": BBS["name"] = a
      yy+=1
      writexy(xx,yy,7,"Enter UserName:")
      a = self.xinput(xx+dd,yy,aa,aa,cs_printable,35,35,' ',BBS['username'])
      if a!="-1": BBS["username"] = a
      yy+=1
      writexy(xx,yy,7,"Enter Password:")
      a = self.xinput(xx+dd,yy,aa,aa,cs_printable,35,35,' ',BBS['password'])
      if a!="-1": BBS["password"] = a
      yy+=1
      writexy(xx,yy,7,"Enter Comment :")
      a = self.xinput(xx+dd,yy,aa,aa,cs_printable,35,35,' ',BBS['comment'])
      if a!="-1": BBS["comment"] = a
      yy+=1
      writexy(xx,yy,7,"Enter Software:")
      a = self.xinput(xx+dd,yy,aa,aa,cs_printable,35,35,' ',BBS['software'])
      if a!="-1": BBS["software"] = a
      yy+=1
      writexy(xx,yy,7,"Enter Location:")
      a = self.xinput(xx+dd,yy,aa,aa,cs_printable,35,35,' ',BBS['location'])
      if a!="-1": BBS["location"] = a
      yy+=1
      
      writexy(xx,yy,7,"Use Sound FXs?")
      BBS["sounds"] = self.getyesno(xx+dd,yy,aa,3*16,7,BBS["sounds"])
      yy+=1
      
      writexy(xx,yy,7,"Is the info entered correct?")
      a = self.getyesno(xx+dd+14,yy,aa,3*16,7,False)
      if a:
        BBS["address"] = HOST+":"+str(PORT)
        BBS['port'] = PORT
        parser = configparser.ConfigParser()
        parser.add_section('BBS-Info')
        for key in BBS.keys():
          parser.set('BBS-Info', key, str(BBS[key]))

        with open(CONFIGDIR + HOST+'.ini', 'w') as f:
          parser.write(f)
        
        break
      writexy(xx,yy,7," "*40)
      xx,yy = 17,10
    
    displayansi(ansimg.BGSCR)
      
    
  def menu(self):
    global ENABLEKEYSOUND,CAPTURE,CAPTUREFILE,BBS
    self.savescreen()
     
    displayansi(ansimg.BGSCR)
    while True:
      xx,yy = 4,8
      writexypipe(xx,yy,7,40-xx,'|14S|08: |07Save BBS'); yy+=1
      writexypipe(xx,yy,7,40-xx,'|14M|08: |07Toggle Sounds [Active:|15{:5}|07]'.format(str(ENABLEKEYSOUND))); yy+=1
      writexypipe(xx,yy,7,40-xx,'|14C|08: |07Toggle Capture [Active:|15{:5}|07]'.format(str(CAPTURE))); yy+=1
      
      yy = 19
      writexy(xx,yy,8,'CTRL-L: Send Login/Password');yy+=1
      writexy(xx,yy,8,'CTRL-R: Find RegEx matches');yy+=1
      writexy(xx,yy,8,'CTRL-C: Hangup and exit program');yy+=1
      writexy(xx,yy,8,'CTRL-A: Save screen to file');yy+=1
      writexy(xx,yy,8,'     B: Back')
      
      xx,yy = 42,8
      writexy(xx,yy,7,'Total Data Transf: {}'.format(str(approximate_size(self.totaldatabytes)))); yy+=1
      dt = datetime.datetime.now()-self.logintime
      writexy(xx,yy,7,'Total Time Logged: {}'.format(str(dt))); yy+=2
      writexy(xx,yy,7,'Name    : {:25.25}'.format(BBS['name'])); yy+=1
      writexy(xx,yy,7,'Address : {:25.25}'.format(BBS['address'])); yy+=1
      writexy(xx,yy,7,'Software: {:20.20}'.format(BBS['software'])); yy+=1
      writexy(xx,yy,7,'Location: {:20.20}'.format(BBS['location'])); yy+=1
      
      
      c = self.kb.getch()
      if c in 'sS':
        self.savebbsmenu()
      elif c in 'mM':
        ENABLEKEYSOUND = not ENABLEKEYSOUND
      elif c in 'cC':
        togglecapture()
      elif c in 'bB': 
        break
    
    self.restorescreen()
    
  
  def run(self):
    global QUITEMODE
    self.totaldatabytes = 0
    self.logintime = datetime.datetime.now()
    ansibuff=""
    data=""
    buff=""
    while True:
      try:
        data = telnet.read_very_eager().decode('cp437')
      except:
        print("\nConnection closed...")
        break
      self.totaldatabytes += len(data)
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
      print("Total data transfer : {}".format(str(approximate_size(self.totaldatabytes))))
      print("Connected at        : {}".format(self.logintime.strftime("%Y/%m/%d (y/m/d), %H:%M:%S")))
      dt = datetime.datetime.now()-self.logintime
      print("Stayed connected for: {}".format(str(dt)))
      print("Average bytes/sec   : {} per sec.".format(str(approximate_size(self.totaldatabytes // dt.total_seconds()))))
        
def parser():
  global HEIGHT,WIDTH,BEEP,CAPTURE,CAPTUREFILE,QUITEMODE,ENABLEKEYSOUND,KBBACKSP
  global HOST,PORT
  res = True
  #parser = argparse.ArgumentParser(description="Telnite // Python3 ANSI-BBS Telnet client for terminal.")
  parser = argparse.ArgumentParser(description=program_descripton, formatter_class=RawFormatter)
  parser.add_argument('-a','--address', metavar='address[:port]',action='store', type=str, help="The telnet address to connect to.")
  parser.add_argument('-w', '--width', dest='width', action='store', metavar='width', help="Force terminal width in chars.")
  parser.add_argument('--height', dest='height', action='store', metavar='height', help="Force terminal height in chars.")
  parser.add_argument('--telnet-guide', dest='guide', action='store', metavar='term', help="Connect to a BBS from the TelnetBBSGuide.")
  parser.add_argument('-l','--list', dest='list', action='store', metavar='term', help="Filter and List saved BBSes to choose from.")
  parser.add_argument('-b','--beep', dest='beep', action='store_true', help="Enable BEEP sound, using SOX.")
  parser.add_argument('-d','--del', dest='delete', action='store_true', help="Use #127/DEL code for backspace.")
  parser.add_argument('-c','--capture', dest='capture', action='store_true', help="Store all incoming ANSI data to file.")
  parser.add_argument('--create-config', dest='config', action='store_true', help="Create a default config file (.ini) in current dir.")
  parser.add_argument('-q','--quite', dest='quite', action='store_true', help="Don't display any app. related text")
  parser.add_argument('--no-sound', dest='nosound', action='store_true', help="Disable all sound FXs")
  args = parser.parse_args()
  
  
  if len(sys.argv) < 2:
    #parser.print_usage()
    parser.print_help()
    sys.exit(1)
  
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
      
    if os.path.isfile(CONFIGDIR + HOST + '.ini'):
      initoBBS(CONFIGDIR + HOST + '.ini')
  
  if args.guide:
    bbstglistselect(args.guide)
  
  if args.list:
    bbslistselect(args.list)
    
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

clrscr()
readconfigfile()
if not parser(): exit()
if HOST=="": exit()

x,y=1,1
init()
ui = UserInterface()

if ENABLEKEYSOUND:
  os.system("play -q "+MODEMSOUND+" >> /dev/null 2>&1 &")
  
try:
  #telnet = telnetlib.Telnet(HOST,port=PORT,timeout=5)
  
  if not QUITEMODE: 
    if BBS['name']!='':
      print("Connecting to {}".format(BBS['name']))
    else:
      print("Connecting to {}".format(HOST))
      
  print("Press CTRL-W for Options and Help...")
  
  telnet.open(HOST,port=PORT,timeout=5)
  #telnet.set_debuglevel(100)
  time.sleep(1)
except:
  telnet.close()
  exit()
  
ui.run()

telnet.close()








