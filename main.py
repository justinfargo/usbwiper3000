import win32com.client, subprocess, sys
from ctypes import *

def watch_usb(): # Watches USB using WMI
    wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\CIMV2")
    query = "SELECT * FROM __InstanceCreationEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBHub'"
    watcher = wmi.ExecNotificationQuery(query)

    print("Watching for USB devices...")

    while True:
        usb_device = watcher.NextEvent()
        drive_letter = usb_device.TargetInstance.Caption.strip()[-1]

        if drive_letter:
            print(f"USB Device Plugged In! ({drive_letter}) ")
            return drive_letter

def scan(drive_letter): # Scans USB device using Windows Defender
	print("Scanner initializing...")
	scanProcess = subprocess.Popen(["powershell.exe", "Start-MpScan -ScanPath " + drive_letter], stdout=sys.stdout) # Initializes scan
	scanProcess.communicate()

def myFmtCallback(command, modifier, arg): # Callback for the wiping function
    print(command)
    return 1    # TRUE

def wipe_usb_drive(drive_letter): # Wiping function
    print("Wipe initializing...")
    fm = windll.LoadLibrary('fmifs.dll')
    FMT_CB_FUNC = WINFUNCTYPE(c_int, c_int, c_int, c_void_p)
    FMIFS_HARDDISK = 0xB
    fm.FormatEx(c_wchar_p(drive_letter + ":"), FMIFS_HARDDISK, c_wchar_p('EXFAT'),
                c_wchar_p('USB'), True, c_int(0), FMT_CB_FUNC(myFmtCallback))

if __name__ == "__main__":
    usb_drive_letter = watch_usb()
    scan(usb_drive_letter)
    wipe_usb_drive(usb_drive_letter)
    print("Finished!")
