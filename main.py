import win32com.client, subprocess

def watch_usb():
    wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\CIMV2")
    query = "SELECT * FROM __InstanceCreationEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBHub'"
    watcher = wmi.ExecNotificationQuery(query)

    print("Watching for USB devices...")

    while True:
        usb_device = watcher.NextEvent()
        drive_letter = usb_device.TargetInstance.Caption.strip()[-1]

        if drive_letter:
            print(f"USB Device Plugged In:")
            print(f"Drive Letter: {drive_letter}")
            print("----------")
            return drive_letter

def wipe_usb_drive(drive_letter):
    try:
        diskpart_script = f"""select disk {drive_letter}
                            clean
                            create partition primary
                            format fs=ntfs quick
                            assign"""
        subprocess.run(["diskpart"], input=diskpart_script, encoding="utf-8", shell=True, check=True)
        print(f"USB Drive ({drive_letter}) has been wiped and formatted.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def scan(drive_letter):
	scanProcess = subprocess.Popen(["powershell.exe", "Start-MpScan -ScanPath " + drive_letter], stdout=sys.stdout) # Initializes scan
	scanProcess.communicate()

if __name__ == "__main__":
    usb_drive_letter = watch_usb()
    drive_letter(usb_drive_letter)
    wipe_usb_drive(usb_drive_letter)



