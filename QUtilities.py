
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
