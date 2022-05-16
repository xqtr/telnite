# telnite

An ANSI-BBS telnet client for use in terminals like Gnome_terminal, xterm,
etc.

Created by XQTR of Another Droid BBS

[] https://github.com/xqtr/telnite
[] telnet://andr01d.zapto.org:9999

Licensed under GPL3

optional arguments:
  -h, --help            show this help message and exit
  -a address[:port], --address address[:port]
                        The telnet address to connect to.
  -w width, --width width
                        Force terminal width in chars.
  --height height       Force terminal height in chars.
  --telnet-guide term   Connect to a BBS from the TelnetBBSGuide.
  -l term, --list term  Filter and List saved BBSes to choose from.
  -b, --beep            Enable BEEP sound, using SOX.
  -d, --del             Use #127/DEL code for backspace.
  -c, --capture         Store all incoming ANSI data to file.
  --create-config       Create a default config file (.ini) in current dir.
  -q, --quite           Don't display any app. related text
  --no-sound            Disable all sound FXs
  
## Features

- Save incoming data/ANSI to a file (capture)
- Save the visible ANSI screen to an ANSI file
- Search visible text for RegEx matches
- Send login credentials with CTRL-L
- Save favorite BBSes to your .config folder and provide different settings for each BBS
- Sound FXs, for connecting to a BBS (modem sound) and keystrokes
- ...perhaps more, that i forgot to mention :)

## USAGE 
  You can use Telnite in **3 different modes**. The simplest is to assign a network address for a BBS and connect to it, by using the -a option.
  
  Example:
  ./telnite -a andr01d.zapto.org:9999
  
  The port number is optional and if is omitted the default telnet port (23) will be used. The second method is to use the --telnet-guide option. This option will provide you with a a list of BBSes, downloaded from the Internet and be able to select one. Because the list is big enough, you have to specify a search term, to filter the results. For example:
'''  
  ./telnite --telnet-guide droid
'''  
  The command above, will download the BBS liste, from Telnet Guide site (telnetbbsguide.com) and search for BBSes containing the word "droid" in their name. The result is something like this:
'''  
Results:
Num) Name                           Address                       :Port 
  0) Android City                   androidcity.retro-os.live     :     
  1) Another Droid BBS              andr01d.zapto.org             :9999 
Select:
'''
Press a number (0/1), with ENTER and you will get connected to that BBS. The third and last mode, is similar to the last option, but is used for your saved/favorite* BBSes. You use the -l option with a search term, to filter results. This option will look into the address of the BBS and not for its name! 

For example:
'''
./telnite -l andr
'''
Will show a result like this:
'''
Results:
Num) Address                       
  0) andr01d.zapto.org             
Select:
'''

*When connected to a BBS you can press CTRL-W and then S to save settings for the currently connected BBS, into your .config folder.*

## In app menu

While running the app. you can press CTRL-W and see a graphical/ANSI menu. This menu will provide you with some info, keyboard shortcuts and also options to select. 

From this menu, you can save a favorite BBS, into your .config folder, toggle sound fxs on/off and toggle capture of incoming data on/off.

