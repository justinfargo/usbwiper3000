from re import L
import win32file, win32api, subprocess, sys, os, win32evtlogutil, win32evtlog, time, threading
from ctypes import *
import tkinter as tk
from tkinter import messagebox

isWiped = []

def scan(letter): # Scans USB device using Windows Defender
    count = sum([len(files) for r, d, files in os.walk(letter)])
    print("Scanning device {0}...".format(letter))
    scanProcess = subprocess.Popen(["powershell.exe", "Start-MpScan -ScanPath " + letter], stdout=sys.stdout) # Initializes scan
    scanProcess.communicate()
    count2 = sum([len(files) for r, d, files in os.walk(letter)])
    if count > count2:
        root = tk.Tk()
        root.withdraw()
        root.iconbitmap(default='blank.ico')
        root.after(5_000, root.destroy)
        tk.messagebox.showwarning(title="", message="A virus has been detected on device {0}!".format(letter))
        win32evtlogutil.ReportEvent(
            "USB Wipe Script",
            1006,   
            eventType=win32evtlog.EVENTLOG_WARNING_TYPE,
            strings=["A virus has been detected."],
            data=b"A virus has been detected.",
        )
        return
    if not letter in isWiped:
        isWiped.append(letter)

def showConfirmationPopup(letter): # Tkinter Interface
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.iconbitmap(default='blank.ico')
    root.after(120_000, root.destroy)
    result = messagebox.askyesno(title="", message="Do you want to wipe device {0}?".format(letter))
    if not result:
        ejectProcess = subprocess.Popen(["powershell.exe", "$driveEject = New-Object -comObject Shell.Application; $driveEject.Namespace(17).ParseName(\"{0}\").InvokeVerb({1})".format(letter, "\"Eject\"")])
        ejectProcess.communicate()
    root.quit()
    return result

def wipeCallback(command, modifier, arg): # Callback for the wiping function
    #print(command)
    return 1    # TRUE

def wipeUSBDrive(letter): # Wiping function
    fm = windll.LoadLibrary('fmifs.dll')
    FMT_CB_FUNC = WINFUNCTYPE(c_int, c_int, c_int, c_void_p)
    FMIFS_HARDDISK = 0xB
    confirmation = showConfirmationPopup(letter)
    if not confirmation:
        print("Cancelled")
        return
    print("Wiping device {0}...".format(letter))
    try:
        fm.FormatEx(c_wchar_p(letter), FMIFS_HARDDISK, c_wchar_p('EXFAT'),
                    c_wchar_p('USB'), True, c_int(0), FMT_CB_FUNC(wipeCallback))
    except:
        print("Error wiping device {0}.".format(letter))
    
    
while True:
    try:
        scannableDevices = []
        drive_list = win32api.GetLogicalDriveStrings()
        drive_list = drive_list.split("\x00")[0:-1]  # the last element is ""
        for letter in drive_list:
            if win32file.GetDriveType(letter) == win32file.DRIVE_REMOVABLE:# check if the drive is of type removable
                scannableDevices.append(letter)
                if not letter in isWiped:
                    scan(letter)
                    wipeUSBDrive(letter)
                    print("Finished...")
        for device in isWiped:
            scannable = False
            for device2 in scannableDevices:
                if device == device2:
                    scannable = True
            if scannable == False:
                isWiped.remove(device)
        
    except Exception as e:
        print("Error... {0}".format(e))