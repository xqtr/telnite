# telnite

An ANSI-BBS telnet client for use in terminals like Gnome_terminal, xterm,etc. It's built to be used as an easy solution for an ANSI telnet client, in Termux and plain/vanilla systems. You just grab it via github (```git clone https://github.com/xqtr/telnite```) and you are ready to go!

Created by XQTR of Another Droid BBS
```
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
```
## Features

- Save incoming data/ANSI to a file (capture)
- Save the visible ANSI screen to an ANSI file
- Search visible text for RegEx matches
- Send login credentials with CTRL-L
- Save favorite BBSes to your .config folder and provide different settings for each BBS
- Sound FXs, for connecting to a BBS (modem sound) and keystrokes
- It is usabe under TERMUX
- ...perhaps more, that i forgot to mention :)

## Usage
  You can use Telnite in **3 different modes**. The simplest is to assign a network address for a BBS and connect to it, by using the -a option.
  
  Example:
  `./telnite -a andr01d.zapto.org:9999`
  
  The port number is optional and if is omitted the default telnet port (23) will be used. The second method is to use the --telnet-guide option. This option will provide you with a a list of BBSes, downloaded from the Internet and be able to select one. Because the list is big enough, you have to specify a search term, to filter the results. For example:
`
  ./telnite --telnet-guide droid
`
  The command above, will download the BBS liste, from Telnet Guide site (telnetbbsguide.com) and search for BBSes containing the word "droid" in their name. The result is something like this:
```
Results:
Num) Name                           Address                       :Port 
  0) Android City                   androidcity.retro-os.live     :     
  1) Another Droid BBS              andr01d.zapto.org             :9999 
Select:
```
Press a number (0/1), with ENTER and you will get connected to that BBS. The third and last mode, is similar to the last option, but is used for your saved/favorite* BBSes. You use the -l option with a search term, to filter results. This option will look into the address of the BBS and not for its name! 

For example:
```
./telnite -l andr
```
Will show a result like this:
```
Results:
Num) Address                       
  0) andr01d.zapto.org             
Select:
```

*When connected to a BBS you can press CTRL-W and then S to save settings for the currently connected BBS, into your .config folder.*

## In app menu

While running the app. you can press CTRL-W and see a graphical/ANSI menu. This menu will provide you with some info, keyboard shortcuts and also options to select. 

From this menu, you can save a favorite BBS, into your .config folder, toggle sound fxs on/off and toggle capture of incoming data on/off.

## Bugs // To Do
Up to this time, the known bugs or so, are:

- If you press multiple times the cursor keys, it may produce an ESC key keystroke
- For debugging purposes no exception handling is used. So you may expirience program crashes, because of bad ANSI escape sequences. Some BBS servers and/or ANSI editors, create ANSI escape sequences that are not valid. In that case Telnite may crash. I have tried to implement many ANSI codes and variable formats of them, but still not all are handled. If you happen to find them, send a note to my email.
- Z/Y/X Modem downloads are not yet implemented... and perhaps it wont be. 
- For better window scrolling, Telnite, uses the ability of the current terminal window to scroll the screen up, when it reaches the bottom. So some, big ANSI files, may not display well, in case there is a mismatch in the terminal size.

## Contact
- Telnet: andr01d.zapto.org:9999
- WWW: andr01d.zapto.org:8080
- Gopher: andr01d.zapto.org:7070
- Email: xqtr@gmx.com

## Changelog
```
2022-05-18: Remove some commented code
            Fixed issue with the dimensions of the terminal
            Removed some unused code from the PyCRT module


```
