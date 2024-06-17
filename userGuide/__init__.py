from .constants import *
import subprocess

from relativePath import RelativePath

HelpState = None
HelpProc = None

def SetHelpState(value):
    global HelpState
    HelpState = value
    
def GetHelpState():
    global HelpState
    return HelpState

def OpenHelp(helpID, reopen: bool = True):
    global HelpProc
    if reopen:
        if HelpProc != None:
            HelpProc.kill()
        HelpProc = subprocess.Popen("hh.exe -mapid" + str(helpID) + " " + RelativePath("help.chm"))
    else:
        subprocess.Popen("hh.exe -mapid" + str(helpID) + " " + RelativePath("help.chm"))
        