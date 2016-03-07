from distutils.core import setup
import distutils.sysconfig
from shutil import rmtree
from os import environ, remove
from sys import argv
from subprocess import Popen
import codecs

VERSION = '1.0-rtl'

DEBUG = False

INSTALL = 1
PACKAGE = 2

def copyFile(src, dest):
    print(src+" -> "+dest)
    try:
        cmd = Popen("copy "+src+" "+dest, shell=True)
    except OSError as ex:
        print("Copy failed: " + ex.strerror)
    rtn = cmd.wait()
    if rtn != 0:
        print("Copy failed.")

def installFiles():
    print("Copying files.")
    copyFile("build\\libs\\i686\\libcocotb.dll", environ['WINDIR'] + "\\System32\\")
    copyFile("build\\libs\\i686\\libgpi.dll", environ['WINDIR'] + "\\System32\\")
    copyFile("build\\libs\\i686\\libgpilog.dll", environ['WINDIR'] + "\\System32\\")
    copyFile("build\\libs\\i686\\libvhpi.dll", environ['WINDIR'] + "\\System32\\")
    copyFile("build\\libs\\i686\\libsim.dll", distutils.sysconfig.PREFIX + "\\DLLs\\simulator.pyd")
    copyFile("lib\\libgcc_s_dw2-1.dll", environ['WINDIR'] + "\\System32\\")

def packageFiles():
    # Run 7-zip to create the archive
    cmdstr = "/cygdrive/c/Program\ Files/7-Zip/7z.exe a dist/cocotb-" + VERSION + ".7z cocotb-" + VERSION
    print("Executing: " + cmdstr)
    try:
        cmd = Popen(cmdstr, shell=True)
        rtn = cmd.wait()
        if rtn != 0:
            print("Command failed.")
    except OSError as ex:
        print("Command failed: " + ex.strerror)
    
    # Create config.txt file
    cfg = codecs.open("dist/config.txt", 'w', 'utf_8_sig')
    cfgstr = ';!@Install@!UTF-8!\n'\
             'Title=\"Cocotb\"\n'\
             'BeginPrompt=\"Do you want to install?\"\n'\
             'ExecuteFile=\".\\\\cocotb-'+VERSION+'\\\\setup.bat\"\n'\
             ';!@InstallEnd@!\n'
    cfg.write(cfgstr)
    cfg.close()

    # create self extracting zip
    cmdstr = "cat 7zS.sfx config.txt cocotb-" + VERSION + ".7z > cocotb-setup-"+ VERSION + ".exe"
    print("Executing: " + cmdstr)
    try:
        cmd = Popen(cmdstr, cwd=".\\dist", shell=True)
        rtn = cmd.wait()
        if rtn != 0:
            print("Command failed.")
    except OSError as ex:
        print("Command failed: " + ex.strerror)

def createBatFile():
    # Create the bat file
    bat = file("setup.bat", "w")
    if DEBUG is not None and DEBUG:
        bat.write("cd cocotb-"+VERSION+"\n"\
                  "setup.py -i\n"\
                  "PAUSE\n")
    else:
        bat.write("cd cocotb-"+VERSION+"\n"\
                  "setup.py -i\n")
    bat.close()

def cleanUp():
    print("Removing temporary files.")
    rmtree("cocotb-"+VERSION)
    remove("dist/cocotb-"+VERSION+".7z")
    remove("dist/cocotb-"+VERSION+".tar.gz")
    remove("dist/config.txt")
    remove("setup.bat")

def runDistutils(args):
   setup(name='cocotb',
         version=VERSION,
         description='Cocotb python simulation envirnoment.',
         packages=['cocotb'],
         script_args=args)

def main():
    action = INSTALL
    if len(argv) < 2:
        # default to install
        action = INSTALL
    else:
        if argv[1] == '-i':
            action = INSTALL
        elif argv[1] == '-p':
            action = PACKAGE
        else:
            print("Unrecognized argument")
            action = INSTALL

    if action == INSTALL:
        print( "Installing cocotb " + VERSION )
        runDistutils(["install"])
        installFiles()
    elif action == PACKAGE:
        print( "Packaging cocotb " + VERSION )
        createBatFile()
        runDistutils(["sdist", "-k"])
        packageFiles()
        cleanUp()
    
if __name__ == '__main__':
    main()
