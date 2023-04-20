
#QUtilities.py


import sys, subprocess
def Pip_Installer(Packages: list[str]) -> None:

    for Package in Packages:
        if Package.lower() in str(subprocess.check_output('pip freeze', stderr=subprocess.STDOUT, shell=True), encoding='utf-8', errors='ignore').lower():
            continue
        print(f'{Colors["Green"]}Installing{Colors["Reset"]} {Package} package...'.ljust(150), end = '')
        try:
            #sys.executable returns python version
            subprocess.run([sys.executable, '-m', 'pip', 'install', Package, '-q'], check=True)
        except subprocess.CalledProcessError as ex:
            Quit(
                ExceptionName = ex,
                Message = f'An {Colors["Red"]}Unknown Error{Colors["Reset"]} came out while trying to download {Package}'
            )
        print(f'[{Colors["Green"]}Done{Colors["Reset"]}]!')

Pip_Installer(Packages=["tqdm"])

import requests, os, urllib, zipfile, shutil, ctypes
from tqdm import tqdm
from time import sleep

# Colors for String formatting :
Colors: dict[str, str] = {
    # "Reset": "\033[0m",
    "Reset": "\033[1;37m",
    "Underline": "\033[1;4m",

    "Grey": "\033[1;30m",
    "Red": "\033[1;31m",
    "Green": "\033[1;32m",
    "Yellow": "\033[1;33m",
    "Blue": "\033[1;34m",
    "Magenta": "\033[1;35m",
    "Cyan": "\033[1;36m",
    "White": "\033[1;37m",
}

DownloadsFolder = os.getcwd() + '\\Adb_Installer\\Downloads\\'
CWDIR = os.getcwd() + '\\Adb_Installer'


def Quit(ExceptionName: Exception, Message: str) -> Exception:
    print('\n' + Message)
    input(f"Press {Colors['Red']}ENTER{Colors['Reset']} to exit : ")
    raise ExceptionName

# Checks if dns exists and can ping a known good server
def isConnected() -> bool:
    print('Running Connection Test...')
    print('Connection Status : ', end = '')
    try:
        urllib.request.urlopen('http://google.com', timeout=2)
        print(f'\t\t[{Colors["Green"]}Online!{Colors["Reset"]}]')
        sleep(2)
        return True
    except urllib.error.URLError:
        print(f'\t\t[{Colors["Red"]}Offline!{Colors["Reset"]}]')
        sleep(2)
        return False

# Checks if the script has Elevated Priviledges only on Windows! In case this program will run on Unix-like systems then need to modify this function 
def isElevated():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except:
        return False

def CheckOSType() -> str:
    if sys.platform == 'win32':
        return True
    return False

def askUser(question: str) -> bool:
    while "the answer is invalid":
        reply = (
            str(input(f'{question}  ({Colors["Green"]}Yes{Colors["Reset"]}/{Colors["Red"]}No{Colors["Reset"]}) : '))
            .lower()
            .strip()
        )
        if reply == "yes": return True
        if reply == "no": return False

#This function adds a path to Windows Environment path and will be removed once the session (program) will be closed
def AddToEnvironmentPath(Directory: str) -> None:
    path = os.environ["PATH"]
    if Directory not in path.split(os.pathsep):
        print(f'\n[{Colors["Green"]}Adding{Colors["Reset"]} {Directory} to the {Colors["Green"]}User Environment{Colors["Reset"]} Path Temporally...]'.ljust(133), end = '')
        os.environ["PATH"] = f"{Directory}{os.pathsep}{path}"
        print(f'[{Colors["Green"]}Done{Colors["Reset"]}!]\n')


def Download(URLink: str, FileName: str, DestinationPath: str = DownloadsFolder, retries: int = 2) -> None:
    """
    URLink: the Direct Download Link of the file to download
    FileName: The name to give to the file once downloaded.         Ex: 'File1.zip'
    DestinationPath: the path where to store the downloaded file    Ex: 'C:/folder1'
    retries: Number of times to try again with the download in case the download didn't end correctly
    
    Download(URLink = 'google.com/DownloadFile.zip', FileName = 'File1.zip')
    """
    try: #Checks if the file that it's going to be downloaded already exists in the destination path, if so then the function breaks (return)
        if FileName in os.listdir(DestinationPath):
            return
    except Exception as ex:
        print('Exception: ', ex)
        input()
        pass

    DestinationPath = DestinationPath + FileName
    try:
        # Sending http request to the direct download link page and showing progress bar as output
        print(f"\n{Colors['Green']}Downloading{Colors['Reset']} {FileName} {Colors['Green']}to{Colors['Reset']} {DestinationPath}")
        response = requests.get(URLink, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 #1 Kibibyte
        progress = tqdm(miniters=1, total=total_size, unit='MB', unit_scale=True, desc=f'{Colors["Green"]}Download progress{Colors["Reset"]}')

        with open(DestinationPath, "wb") as file:
            for data in response.iter_content(block_size):
                progress.update(len(data))
                file.write(data)

        progress.close()
        print(f"{Colors['Red']} -> {Colors['Reset']}[{Colors['Green']}Done{Colors['Reset']}!]\n")

    except requests.exceptions.ConnectionError:  # If the download has been interrupted for Connection Lost or the connection was Forcibly closed
        print(f"{Colors['Red']}Failed{Colors['Reset']} to download {FileName}...")
        if not isConnected():
            print("\t[Please make sure you are connected to Internet!]")
            input(
                f"Press {Colors['Red']}ENTER{Colors['Reset']} key if you are connected to Internet : "
            )  # This input is like a delay : when the user is correctly connected to internet then the program will continue
            
            Download(URLink, FileName)

        elif (
            isConnected()
        ):  # If the connection is stable then the connection was Forcibly closed by AntiVirus or an other process.
            print("\t[The download process has been stopped from an unknown source!]")
        if retries > 0:
            Download(URLink, FileName, retries - 1)
    except Exception as ex:
        Quit(ExceptionName = ex, Message = f"{FileName} failed to be downloaded for some reason.")


# Gets zip file name and extracts its contents inside a path : Zip_FileName = 'Ajk.zip', DestinationPath = DestinationPath -> inside DestinationPath will be extracted all files
def ExtractZip(Zip_FileName: str, DestinationPath: str, HasFolderInside: bool, Rename: bool = False):

    ListDir_Before = set(os.listdir(DestinationPath))
    Zip_Path = DownloadsFolder + Zip_FileName
    
    #Checks whatever the zip file already exists in the destination path. If so then return.
    if Zip_FileName[:-4] in os.listdir(DestinationPath):
        return

    if not HasFolderInside:
        DestinationPath += Zip_FileName[:-4]
        
    print(f"\n{Colors['Green']}Extracting{Colors['Reset']} {Zip_FileName} {Colors['Green']}to{Colors['Reset']} {DestinationPath}")

    with zipfile.ZipFile(Zip_Path, "r") as zip_ref:
        try:
            zip_ref.extractall(path = DestinationPath, pwd = None, members = tqdm(zip_ref.infolist(), unit='MB', desc = f'{Colors["Green"]}Extraction progress{Colors["Reset"]}'))
        except zipfile.error as ex:
            Quit(
                ExceptionName = ex, 
                Message = f'{Colors["Red"]}Cannot{Colors["Reset"]} Extract {Zip_FileName}!'
            )
        except Exception as ex:
            Quit(
                ExceptionName = ex, 
                Message = f'{Colors["Red"]}Cannot{Colors["Reset"]} Extract {Zip_FileName} for unknown reasons!'
            )

    ListDir_After = set(os.listdir(DestinationPath))
    if Rename and HasFolderInside:
        Extracted_FolderName = list(ListDir_After - ListDir_Before)[0]
        os.replace(DestinationPath + Extracted_FolderName, DestinationPath + Zip_FileName[:-4])

    print(f"{Colors['Red']} -> {Colors['Reset']}[{Colors['Green']}Done{Colors['Reset']}!]\n")
    

def CheckFile(Filename: str, Directory = f'{os.getcwd()}\\') -> bool:
    """This function returns True or False in case a file is in a specific directory. If the directory doesn't exists, it returns False."""
    return os.path.isfile(Directory + '\\' + Filename)

# Checks if whatever executable provided (as string) exists in $PATH
def checkTool(name: str, path: str = '') -> bool:
    if path:
        return CheckFile(Filename=name, Directory=path)
    return shutil.which(name) is not None










#Installer.py

def Terminal__Init__():
    """This function initialize terminal style and preferences such as GUI, description, size etc..."""
    os.system('color 07 && cls') #Executing this (any command) will fix any possible ANSI Characters issues (Colors)
    # os.system('mode con cols=123 lines=30 && color 07 && cls') #Setting terminal window size and default color (White on black)
    if not CheckOSType():
        Quit(
            ExceptionName=SystemExit,
            Message=f"The program works only for {Colors['Red']}Windows 10{Colors['Reset']}!\nPlease, make sure that you run this program (or shell) an a Windows 10 computer!"
        )
    if not isElevated():
        Quit(
            ExceptionName=SystemExit,
            Message=f"The program {Colors['Red']}has not been executed with Admin rights{Colors['Reset']}!\nPlease, make sure that you run this program (or shell) as Administrator!"
        )
    if not isConnected():
        Quit(
            ExceptionName=SystemExit,
            Message=f"The {Colors['Red']}internet{Colors['Reset']} connection doesn't work!\nPlease, make sure that your internet connection works in order to correctly download the tools!"
        )
    os.system('mode con cols=125 lines=32 && cls') #Setting terminal window size and default color (White on black)

    global Android_adb_Logo
    Android_adb_Logo = rf"""{Colors["Green"]}
                                                                                                 #Tool developed by @Quantum
                                                                                                        #GitHub: QuantumNone
    
                ^^                        .^:         {Colors["Reset"]}      _____               .___                .__     .___ {Colors["Green"]}
                :!~.                     .!!.         {Colors["Reset"]}     /  _  \    ____    __| _/_______   ____  |__|  __| _/ {Colors["Green"]}
                 .~!.   ..:::^^::::..   :!~.          {Colors["Reset"]}    /  /_\  \  /    \  / __ | \_  __ \ /  _ \ |  | / __ |  {Colors["Green"]}
                   ~7~~!!77777777777!!~~7^            {Colors["Reset"]}   /    |    \|   |  \/ /_/ |  |  | \/(  <_> )|  |/ /_/ |  {Colors["Green"]}
                .^!!777777777777777777777!~^.         {Colors["Reset"]}   \____|__  /|___|  /\____ |  |__|    \____/ |__|\____ |  {Colors["Green"]}
              :~77777777777777777777777777777~.       {Colors["Reset"]}           \/      \/      \/                          \/  {Colors["Green"]}
            .~777777777777777777777777777777777~.     {Colors["Reset"]}                             .______.                      {Colors["Green"]}
           :!777777:.:!777777777777777!:.^777777!:    {Colors["Reset"]}                 _____     __| _/\_ |__                    {Colors["Green"]}
          :77777777^.:!777777777777777!:.^77777777:   {Colors["Reset"]}                 \__  \   / __ |  | __ \                   {Colors["Green"]}
         .7777777777777777777777777777777777777777!.  {Colors["Reset"]}                  / __ \_/ /_/ |  | \_\ \                  {Colors["Green"]}
         ~77777777777777777777777777777777777777777^  {Colors["Reset"]}                 (____  /\____ |  |___  /                  {Colors["Green"]}
        .~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^  {Colors["Reset"]}                      \/      \/      \/                   {Colors["Green"]}
                                                 
        {Colors["Reset"]}"""

    print(Android_adb_Logo)
    print('Welcome to Android adb!')
    print('This tool will correctly install Adb&Fastboot tools and will also install USB Drivers!!\n')
    input(f'Press {Colors["Green"]}ENTER{Colors["Reset"]} key to continue with the installation: \n{Colors["Green"]}>>>{Colors["Reset"]} ')


def WorkSpace_Setup():
    """Removes any existsing workspace and creates a new one (Adb_Installer in os.getcwd()). It also removes unstable adb drivers."""
    print(f'[{Colors["Green"]}Premiliminaries{Colors["Reset"]}: creating workspace...]')
    print(f'\t{Colors["Red"]}Deleting{Colors["Reset"]} installed Adb binaries...'.ljust(120), end = '', flush=True)
    if os.path.exists('C://platform-tools'):
        try:
            subprocess.check_output('rmdir /S /Q C://platform-tools', stderr = subprocess.STDOUT, shell=True) #Deletes platform-tools folder and his sub-files in quiet mode
        except: pass
    print(f"[{Colors['Green']}Done{Colors['Reset']}!]")

    print(f'\t{Colors["Red"]}Uninstalling{Colors["Reset"]} unstable Adb drivers...'.ljust(120), end = '', flush=True)
    output = str(subprocess.check_output('Dism /Online /get-drivers /Format:list', stderr = subprocess.STDOUT, shell=True), encoding='utf-8', errors='ignore').split('\r\n\r\n')
    for oem in output:
        #Output:
        # Published Name : oem58.inf
        # Original File Name : android_winusb.inf
        # Inbox : No
        # Class Name : AndroidUsbDeviceClass
        # Provider Name : Google, Inc.
        # Date : 8/28/2014
        # Version : 11.0.0.0
        try:
            Published_Name = oem.split('\n')[0].split(' : ')
            Provider_Name = oem.split('\n')[4].split(' : ')
            if 'Google, Inc.' in Provider_Name: #There might be more than 1 oem installed as 'Google, Inc.'. That's why we loop.
                subprocess.check_output(f'PNPUtil.exe /delete-driver {Published_Name} /uninstall /force', stderr = subprocess.STDOUT, shell=True)
        except:
            pass
    print(f"[{Colors['Green']}Done{Colors['Reset']}!]")

    # print(f'\t{Colors["Red"]}Removing{Colors["Reset"]} existing workspaces...'.ljust(120), end = '', flush=True)      #Maybe this can be removed as it's useless to continue deleting files if the program  is run more than 1 time
    # if os.path.exists(os.getcwd() + '\\Adb_Installer'):
    #     subprocess.check_output(f'rmdir /Q /S {os.getcwd()}\\Adb_Installer > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
    # print(f"[{Colors['Green']}Done{Colors['Reset']}!]")

    print(f'\t{Colors["Green"]}Creating{Colors["Reset"]} Adb_Installer workspace...'.ljust(120), end = '', flush=True)
    try:
        os.mkdir('Adb_Installer')
    except: pass
    os.chdir(os.getcwd() + '\\Adb_Installer')
    try:
        os.mkdir('Downloads')
    except: pass
    print(f"[{Colors['Green']}Done{Colors['Reset']}!]")


def Install_AdbFastboot():
    Download(
        URLink = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
        FileName = "platform-tools.zip"
    )

    ExtractZip(
        Zip_FileName = "platform-tools.zip",
        DestinationPath = DownloadsFolder, #The program has to be executed with Admin rights
        HasFolderInside = True # -> "platform-tools"
    )

    Download(
        URLink = "https://dl.google.com/android/repository/usb_driver_r13-windows.zip",
        FileName = "usb_driver.zip"
    )

    ExtractZip(
        Zip_FileName = "usb_driver.zip",
        DestinationPath = DownloadsFolder,
        HasFolderInside = True, #-> "usb_driver"
    )


def Install_AdbDrivers():
    """Downloads the files required to 'patch' android_winusb.inf driver file, signs it and installs it. Current Working Directory returned : ./Adb_Installer"""
    print(f'\n\n[{Colors["Green"]}Premiliminaries{Colors["Reset"]}: downloading essential Tools...]')
    
    #All these files could just be packed all in a zip file but the permanent download link would be very long with Google Drive. We keep them also to give credits to its creator : Fawaz Ahmed
    Download(
        URLink = "https://cdn.jsdelivr.net/gh/fawazahmed0/Latest-adb-fastboot-installer-for-windows@master/files/google64inf",
        DestinationPath = DownloadsFolder,
        FileName = "google64inf"
    )
    Download(
        URLink = "https://cdn.jsdelivr.net/gh/fawazahmed0/Latest-adb-fastboot-installer-for-windows@master/files/google86inf",
        DestinationPath = DownloadsFolder,
        FileName = "google86inf"
    )
    Download(
        URLink = "https://cdn.jsdelivr.net/gh/fawazahmed0/Latest-adb-fastboot-installer-for-windows@master/files/Stringsvals",
        DestinationPath = DownloadsFolder,
        FileName = "Stringsvals"
    )
    Download(
        URLink = "https://cdn.jsdelivr.net/gh/fawazahmed0/Latest-adb-fastboot-installer-for-windows@master/files/kmdf",
        DestinationPath = DownloadsFolder,
        FileName = "kmdf"
    )
    Download(
        URLink = "https://cdn.jsdelivr.net/gh/fawazahmed0/Latest-adb-fastboot-installer-for-windows@master/files/fetch_hwidps1",
        DestinationPath = DownloadsFolder,
        FileName = "Fetch_HwID.ps1"
    )
    Download(
        URLink = "https://cdn.jsdelivr.net/gh/fawazahmed0/Latest-adb-fastboot-installer-for-windows@master/files/devconexe",
        DestinationPath = DownloadsFolder,
        FileName = "devcon.exe"
    )

    def Driver_Signer():
        print(f'\t{Colors["Green"]}Killing{Colors["Reset"]} Adb services...'.ljust(120), end = '', flush=True)
        subprocess.check_output('adb kill-server > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
        print(f"[{Colors['Green']}Done{Colors['Reset']}!]")
        
        os.chdir(DownloadsFolder)
        print(f'\t{Colors["Red"]}Executing{Colors["Reset"]} Fetch_HwID.ps1 script...'.ljust(120), end = '', flush=True)
        subprocess.check_output(f'powershell -executionpolicy bypass {DownloadsFolder}\\Fetch_HwID.ps1', stderr=subprocess.STDOUT, shell = True)
        print(f"[{Colors['Green']}Done{Colors['Reset']}!]")

        print(f'\t{Colors["Green"]}Patching{Colors["Reset"]} android_winubs.inf driver file...'.ljust(120), end = '', flush=True)
        #Current Path: Adb_Installer/Downloads/ 
        subprocess.check_output('powershell -executionpolicy bypass -Command "gc Stringsvals | Add-Content usb_driver\\android_winusb.inf"', stderr=subprocess.STDOUT, shell = True)
        subprocess.check_output('powershell -executionpolicy bypass -Command "(gc usb_driver\\android_winusb.inf | Out-String) -replace \'\[Google.NTamd64\]\', (gc google64inf | Out-String) | Out-File usb_driver\\android_winusb.inf"', stderr=subprocess.STDOUT, shell = True)
        subprocess.check_output('powershell -executionpolicy bypass -Command "(gc usb_driver\\android_winusb.inf | Out-String) -replace \'\[Google.NTx86\]\', (gc google86inf | Out-String) | Out-File usb_driver\\android_winusb.inf"', stderr=subprocess.STDOUT, shell = True)
        subprocess.check_output('powershell -executionpolicy bypass -Command "(gc usb_driver\\android_winusb.inf | Out-String) -replace \'\[Strings\]\', (gc kmdf | Out-String) | Out-File usb_driver\\android_winusb.inf"', stderr=subprocess.STDOUT, shell = True)
        print(f"[{Colors['Green']}Done{Colors['Reset']}!]")

        Download(
            URLink = "https://cdn.jsdelivr.net/gh/fawazahmed0/windows-unsigned-driver-installer@master/files.zip",
            FileName = "Driver_Signing.zip"
        )
        ExtractZip(
            Zip_FileName = "Driver_Signing.zip",
            DestinationPath = DownloadsFolder + 'usb_driver\\',
            HasFolderInside = True,
            Rename = True
        )
        os.chdir(os.getcwd() + '\\usb_driver')
        #Current Path: Adb_Installer/Downloads/usb_driver
        print(f'\t{Colors["Red"]}Signing{Colors["Reset"]} android_winubs.inf driver file...'.ljust(120), end = '', flush=True)
        subprocess.check_output(r'Driver_Signing\inf2cat.exe /driver:. /os:7_X64 > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
        subprocess.check_output(r'Driver_Signing\inf2cat.exe /driver:. /os:7_X86 > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
        subprocess.run(r'Driver_Signing\SignTool.exe sign /f Driver_Signing\myDrivers.pfx /p testabc /t http://timestamp.verisign.com/scripts/timstamp.dll /v *.cat > nul 2>&1', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[{Colors['Green']}Done{Colors['Reset']}!]")

        print(f'\t{Colors["Green"]}Adding{Colors["Reset"]} the Certificates...'.ljust(120), end = '', flush=True)
        subprocess.check_output(r'Driver_Signing\CertMgr.exe -add Driver_Signing\myDrivers.cer -s -r localMachine ROOT > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
        subprocess.check_output(r'Driver_Signing\CertMgr.exe -add Driver_Signing\myDrivers.cer -s -r localMachine TRUSTEDPUBLISHER > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
        print(f"[{Colors['Green']}Done{Colors['Reset']}!]")
        
        print(f'\t{Colors["Red"]}Disabling{Colors["Reset"]} Driver Signature Enforcement...'.ljust(120), end = '', flush=True)
        subprocess.check_output(r'bcdedit /set testsigning on', stderr = subprocess.STDOUT, shell=True)
        print(f"[{Colors['Green']}Done{Colors['Reset']}!]")

        print(f'\t{Colors["Green"]}Installing{Colors["Reset"]} the patched driver...'.ljust(120), end = '', flush=True)
        # try:
        subprocess.check_output(r'PNPUtil.exe -i -a android_winusb.inf > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
        # except: pass
        # subprocess.check_output(r'PNPUtil.exe /scan-devices', stderr = subprocess.STDOUT, shell=True)
        print(f"[{Colors['Green']}Done{Colors['Reset']}!]")
        
        print(f'\t{Colors["Red"]}Removing{Colors["Reset"]} the Certificates...'.ljust(120), end = '', flush=True)
        subprocess.check_output(r'Driver_Signing\CertMgr.exe -del -c -n "Fawaz Ahmed" -s -r localMachine ROOT > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
        subprocess.check_output(r'Driver_Signing\CertMgr.exe -del -c -n "Fawaz Ahmed" -s -r localMachine TrustedPublisher > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
        print(f"[{Colors['Green']}Done{Colors['Reset']}!]")

        print(f'\t{Colors["Green"]}Enabling{Colors["Reset"]} Driver Signature Enforcement...'.ljust(120), end = '', flush=True)
        subprocess.check_output(r'bcdedit /set testsigning off', stderr = subprocess.STDOUT, shell=True)
        print(f"[{Colors['Green']}Done{Colors['Reset']}!]")
        
        os.chdir(CWDIR)

    Driver_Signer()
    if not os.path.exists('C:/platform-tools'):
        os.system(f'copy /Y {DownloadsFolder}platform-tools C:/ > nul 2>&1') #Just need permanent Path to environment as by execute AddToEnvironmentPath() will be added until the program finishes.

    AddToEnvironmentPath(Directory='C:/platform-tools')
    print(f'\t{Colors["Green"]}Rebooting{Colors["Reset"]} phone into bootloader...'.ljust(120), end = '', flush=True)
    Connection = str(subprocess.check_output(f'{DownloadsFolder}platform-tools/adb.exe reboot bootloader', stderr = subprocess.STDOUT, shell=True), encoding='utf-8', errors='ignore')
    print(f"[{Colors['Green']}Done{Colors['Reset']}!]")
    if 'unauthorized' in Connection:
        SetupDeviceForUSBCommunication()
        Connection = str(subprocess.check_output(f'{DownloadsFolder}platform-tools/adb.exe reboot bootloader', stderr = subprocess.STDOUT, shell=True), encoding='utf-8', errors='ignore')
    
    print(f'[{Colors["Red"]}Waiting{Colors["Reset"]} for the phone to reboot in Fastboot Mode...]'.ljust(127), end = '', flush=True)
    while True:
        try:
            Fastboot_Connection = str(subprocess.check_output('PNPUtil.exe /enum-devices /problem 28', stderr = subprocess.STDOUT, shell=True), encoding='utf-8', errors='ignore') #This command waits for the device to be in Fastboot Mode. Once in, it returns the control back to Android adb
            if 'USB' in Fastboot_Connection:
                break
            sleep(2)
        except: pass
        if 'ADB Interface' in str(subprocess.check_output('PNPUtil.exe /enum-devices | findstr ADB', stderr = subprocess.STDOUT, shell=True), encoding='utf-8', errors='ignore'):
            #The drivers are already installed but need to ensure that fastboot works : 
            Fastboot_Connection = str(subprocess.check_output(f'{DownloadsFolder}platform-tools/fastboot.exe devices', stderr = subprocess.STDOUT, shell=True), encoding='utf-8', errors='ignore')
            if 'devices' in Fastboot_Connection:
                break #IF not then the program will continue looping... Cannot uninstall the driver while in use...

    print(f"[{Colors['Green']}Done{Colors['Reset']}!]")
    
    Driver_Signer()

    subprocess.check_output(f'{DownloadsFolder}platform-tools/adb.exe kill-server > nul 2>&1', stderr = subprocess.STDOUT, shell=True)
    subprocess.check_output(f'{DownloadsFolder}platform-tools/fastboot.exe getvar all', stderr = subprocess.STDOUT, shell=True)
    Connection = str(subprocess.check_output(f'{DownloadsFolder}platform-tools/fastboot.exe devices', stderr = subprocess.STDOUT, shell=True), encoding='utf-8', errors='ignore')
    print(f'\t{Colors["Green"]}Rebooting{Colors["Reset"]} phone into bootloader...'.ljust(120), end = '', flush=True)
    Connection = str(subprocess.check_output(f'{DownloadsFolder}platform-tools/fastboot.exe reboot', stderr = subprocess.STDOUT, shell=True), encoding='utf-8', errors='ignore')
    print(f"[{Colors['Green']}Done{Colors['Reset']}!]")
    try:
        os.system(f'rmdir /Y /Q {DownloadsFolder}usb-driver')
    except: pass

    ExtractZip(
        Zip_FileName = "usb_driver.zip",
        DestinationPath = DownloadsFolder,
        HasFolderInside = True, #-> "usb_driver"
    )

# The user has to follow these steps in order to be able to use Adb
def SetupDeviceForUSBCommunication():
    print(f'''

    1. Open your device {Colors["Green"]}settings{Colors["Reset"]} and navigate into "About my phone" option.
    2. Search for "{Colors["Red"]}Build number{Colors["Reset"]}" option inside these settings (if you cannot find it try in "{Colors["Green"]}Software Information{Colors["Reset"]}" option).
    3. Tap 7 times on "Build number" option to enable {Colors["Red"]}Developer Options{Colors["Reset"]}.        ["{Colors["Green"]}Build Number{Colors["Reset"]}" or "{Colors["Green"]}MIUI version{Colors["Reset"]}"]
    4. Go back to settings and {Colors["Red"]}search{Colors["Reset"]} for Developer Options.
    5. Search for "{Colors["Red"]}USB debugging{Colors["Reset"]}" option and {Colors["Green"]}enable{Colors["Reset"]} it.
    6. {Colors["Green"]}Connect{Colors["Reset"]} now your device to your computer trough USB cable and check your device screen.
    7. {Colors["Green"]}Allow{Colors["Reset"]} the pop-up asking for computer permissions.
    8. Now search inside Developer Options for "{Colors["Red"]}Select USB configuration{Colors["Reset"]}".
    9. Click it and select "{Colors["Green"]}MTP File transfer{Colors["Reset"]}" protocol.'''
    )

    input(f'\n\t=> Press {Colors["Green"]}Enter{Colors["Reset"]} key to continue : ')

    print(f'\n    10. Now search for "{Colors["Red"]}OEM Unlocking{Colors["Reset"]}" option in Developer options and {Colors["Green"]}ENABLE{Colors["Reset"]} it!')
    print(
        f'''
        {Colors["Red"]}IF{Colors["Reset"]} YOU CANNOT FIND THAT OPTION THEN LOOK AT THESE DOCUMENTATIONS :
            1. Missing "OEM Unlocking" option : 
                           "{Colors["Blue"]}https://krispitech.com/fix-the-missing-oem-unlock-in-developer-options/{Colors["Reset"]}"
            2. "OEM Unlocking" shows "Connect to the internet or contact your carrier" : 
                           "{Colors["Blue"]}https://www.quora.com/Why-do-some-mobile-companies-refuse-to-unlock-bootloaders-like-Huawei-and-Realme{Colors["Reset"]}"
        
        If that option is enabled and {Colors["Grey"]}greyed out{Colors["Reset"]}, it means that the phone's bootloader is already unlocked!
        '''
        )

    input(f'\n\t=> Press {Colors["Green"]}Enter{Colors["Reset"]} key to continue : ')

    
    print(f'''

    If this message comes out on your Android's screen then allow it:
        {Colors["Green_Highlight"]}Allow USB debugging? {Colors["Reset"]}
        {Colors["Green_Highlight"]}The computer's RSA key fingerprint is :{Colors["Reset"]}
        {Colors["Green_Highlight"]}1B:28:11:B0:AC:F4:E6:1E:01:0D {Colors["Reset"]}           [For example]
        {Colors["Green"]}☑ {Colors["Reset"]}{Colors["Green_Highlight"]}Always allow from this computer {Colors["Reset"]}
                    cancel  {Colors["Green"]}OK{Colors["Reset"]}

    ''')
    print()


def Terminal__Quit__(): #Saying all is installed, the path of Adb&fastboot etc...
    os.system('cls')
    print(Android_adb_Logo)
    print(f"\n[{Colors['Green']}Status{Colors['Reset']}]: The program has finished {Colors['Green']}Adb&Fastboot{Colors['Reset']} installation and correctly installed {Colors['Green']}USB drivers{Colors['Reset']}!")
    print(f"[{Colors['Green']}Adb Path{Colors['Reset']}]: {Colors['Blue']}C:/platform-tools{Colors['Reset']}")
    print(f"[{Colors['Green']}Driver Name{Colors['Reset']}]: Android Composite ADB Interface")
    print(f"[{Colors['Green']}Temp Files{Colors['Reset']}]: {Colors['Blue']}{os.getcwd()}{Colors['Reset']}")

    input(f'\n\t=> Press {Colors["Green"]}Enter{Colors["Reset"]} key to Quit : ')


if __name__ == '__main__': #If it's been executed as a script:
    Terminal__Init__()
    WorkSpace_Setup()
    Install_AdbFastboot()
    Install_AdbDrivers()
    Terminal__Quit__()
