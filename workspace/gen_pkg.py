#encoding=utf8
import os, sys, re
if not os.getcwd() in sys.path: # fix linux 软连接的 bug
    sys.path.append(os.getcwd())

from pythonx.funclib import *
from pythonx.pelib import *
from pythonx.mytoolspub import *
import argparse
mydll = getMyDll()

forTONG = "forTONG" in sys.argv

def mainGenExe(keydir, winp=""):
    subdir = keydir
    if forTONG: # 文件检查（跳过）
        pass # assert not winp, winp
    elif winp:
        subdir = keydir + "_" + winp

    rcfile = subdir + ".rc"
    if not os.path.exists(rcfile):
        return False

    rclist = readfileLines(rcfile)
    loader2019 = "loader2\\kinstaller.exe"
    if forTONG:
        loader2019 = "loader2\\winstaller.exe"

    targetfile = keydir + ".exe"
    ResourceHacker = getFileTool("ResourceHacker.exe")
    osremove(targetfile)

    script = r"""
[FILENAMES]
Exe={}
SaveAs={}
Log=logfile.txt

[COMMANDS]""".format(loader2019, targetfile)
    for line in rclist:
        line = line.strip()
        if not line: continue
        # ZLOADER_ROOT_JSON RCDATA "pecopy.json"
        KEY, RCDATA, PATH = line.split(maxsplit=2)
        PATH = PATH.strip()[1:-1].replace("\\\\", "\\")
        cmdx = r"""
-addoverwrite {}, RCData,{},1033""".format(PATH, KEY)
        script += cmdx

    scriptfile = "{}.script.txt".format(subdir)
    script = script.replace("\r\n", "\n").replace("\n", "\r\n")
    script = script.strip() + "\r\n"
    writefile(scriptfile, script)
    cmdx = r"""{} -script {}""".format(ResourceHacker, scriptfile)
    print(cmdx)
    os.system(cmdx)
    osremove(scriptfile)
    osremove("logfile.txt")
    return True

# exename:
# iconname: ..\image\icon\
def getRepIconCmdx(exename, iconname, mcp=False):
    cmdx = r"..\..\dist\pecopy.exe -in {} -out ..\..\dist\{} -icon ..\image\icon\{} -mask {}".format(
        exename, exename, iconname, r"ICONGROUP,MAINICON,0;ICONGROUP,107,2052;ICONGROUP,108,2052")

    if os.path.exists(r"F:\pythonx\pecopy.py"):
        cmdx = r"python3 F:\pythonx\pecopy.py -in {} -out ..\..\dist\{} -icon ..\image\icon\{} -mask {}".format(
            exename, exename, iconname, r"ICONGROUP,MAINICON,0;ICONGROUP,107,2052;ICONGROUP,108,2052")

    if forTONG: # 设置为 GUI
        cmdx += " -gui 1"

    if mcp:
        cmdx += " -mcp 65001"
    return cmdx

def parse_args():
    parser = argparse.ArgumentParser(description=__file__)
    parser.add_argument('--app', type=str, default='', help='app name', required=True)
    parser.add_argument('--icon', type=str, default='', help='icon file', required=True)
    parser.add_argument('--mcp', type=bool, default=False, help='mcp code')
    args = parser.parse_args()
    return args

# kinstaller.exe -in kinstaller.exe -out loader20192.exe -mcp 65001 -debug 1
if __name__ == "__main__":

    args = parse_args()
    print(args.app, args.icon, args.mcp)

    if "pecopy" in sys.argv:
        mainGenExe("pecopy", getPlatform())
        # -mcp 65001 -- win10x64 不需要这玩意。
        cmdx = r"pecopy.exe -mcp 65001 -in pecopy.exe -out ..\..\dist\pecopy.exe -icon ..\image\icon\iconall\shitou.ico -mask ICONGROUP,MAINICON,0;ICONGROUP,107,2052;ICONGROUP,108,2052"
        print("***" * 30)
        print(cmdx)
        os.system(cmdx)

    elif "test" in sys.argv:
        mainGenExe("test", getPlatform())
        cmdx = r"test\test.exe -in test.exe -out test2.exe -mcp 65001 -debug 1"
        print("***" * 30)
        print(cmdx)
        os.system(cmdx)

    else:
        mainGenExe(args.app, getPlatform())
        cmdx = getRepIconCmdx(args.app+r".exe", args.icon, args.mcp)
        print("***" * 30)
        print(cmdx)
        os.system(cmdx)
