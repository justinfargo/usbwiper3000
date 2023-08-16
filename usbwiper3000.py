import win32file, win32api, subprocess, sys, os, win32evtlogutil, win32evtlog
from ctypes import *
from time import sleep
import tkinter as tk
from tkinter import messagebox

wipedYes = []

def scan(letter): # Scans USB device using Windows Defender
    count = sum([len(files) for r, d, files in os.walk(letter)])
    print("Scanning device {0}...".format(letter))
    scanProcess = subprocess.Popen(["powershell.exe", "Start-MpScan -ScanPath " + letter], stdout=sys.stdout) # Initializes scan
    scanProcess.communicate()
    count2 = sum([len(files) for r, d, files in os.walk(letter)])
    if count != count2:
        root = tk.Tk()
        root.withdraw()
        root.iconbitmap(default='blank.ico')
        tk.messagebox.showwarning(title="", message="A virus has been detected on device {0}!".format(letter))
        win32evtlogutil.ReportEvent(
            "USB Wipe Script",
            1006,   
            eventType=win32evtlog.EVENTLOG_WARNING_TYPE,
            strings=["A virus has been detected."],
            data=b"A virus has been detected.",
    )
    if not letter in wipedYes:
        wipedYes.append(letter)

def showConfirmationPopup(letter):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.iconbitmap(default='blank.ico')
    result = messagebox.askyesno(title="", message="Do you want to wipe device {0}?".format(letter))
    return result

def myFmtCallback(command, modifier, arg): # Callback for the wiping function
    return 1    # TRUE

def wipeUSBDrive(letter): # Wiping function
    confirmation = showConfirmationPopup(letter)
    if not confirmation:
        print("Cancelled")
        return
    print("Wiping device {0}...".format(letter))
    fm = windll.LoadLibrary('fmifs.dll')
    FMT_CB_FUNC = WINFUNCTYPE(c_int, c_int, c_int, c_void_p)
    FMIFS_HARDDISK = 0xB
    try:
        fm.FormatEx(c_wchar_p(letter), FMIFS_HARDDISK, c_wchar_p('EXFAT'),
                    c_wchar_p('USB'), True, c_int(0), FMT_CB_FUNC(myFmtCallback))
    except:
        print("Error wiping device {0}.".format(letter))

while True:
    try:
        drive_list = win32api.GetLogicalDriveStrings()
        drive_list = drive_list.split("\x00")[0:-1]  # the last element is ""
        scanableDevices = []
        for letter in drive_list:
            if win32file.GetDriveType(letter) == win32file.DRIVE_REMOVABLE:# check if the drive is of type removable
                scanableDevices.append(letter)
                if not letter in wipedYes:
                    scan(letter)
                    wipeUSBDrive(letter)
                    print("Finished...")
        for device in wipedYes:
            scannable = False
            for device2 in scanableDevices:
                if device == device2:
                    scannable = True
            if scannable == False:
                wipedYes.remove(device)
        
    except Exception as e:
        print("Error... {0}".format(e))