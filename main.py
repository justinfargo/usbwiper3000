import subprocess, sys, win32evtlogutil
from ctypes import *

checkDisc = subprocess.check_output('wmic logicaldisk get DriveType, caption', shell=True) ## Reads connected disks
wipable = None
count = 0

for drive in str(checkDisc).strip().split('\\r\\r\\n'): # Filters through list
    if '2' in drive:
        drive_letter = drive.split(':')[0] # Gets drive letter
        drive_type = drive.split(':')[1].strip() # Gets drive type (Not needed?)
        
        if drive_type == '2': 
            wipable = True #Sets value of wipable (above) to true

path = drive_letter + ":" # Sets drive path of device to scan
quickScan = subprocess.Popen(["powershell.exe", "Start-MpScan -ScanPath " + path], stdout=sys.stdout) # Initializes scan
quickScan.communicate() # Returns output of process

""" if quickScan == True: # if scanner returns virus? to-do!
    win32evtlogutil.ReportEvent("USBDetect", "0619", "1", strings="A virus has been detected.")

"""
def myFmtCallback(command, modifier, arg):
    print(command)
    return 1    # TRUE

def format_drive():
    fm = windll.LoadLibrary('fmifs.dll')
    FMT_CB_FUNC = WINFUNCTYPE(c_int, c_int, c_int, c_void_p)
    FMIFS_HARDDISK = 0xB
    fm.FormatEx(c_wchar_p(path), FMIFS_HARDDISK, c_wchar_p('FAT32'),
                c_wchar_p('USB' + str(count)), True, c_int(0), FMT_CB_FUNC(myFmtCallback))
    
win32evtlogutil.ReportEvent(
    appName= "USBDetect", 
    eventID= 10, 
    eventCategory=0,
    strings= ["A virus has been detected on device " + drive_letter + "." + "\nThis event will be logged and reported."])

format_drive()