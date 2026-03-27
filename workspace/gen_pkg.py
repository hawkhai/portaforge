#encoding=utf8
import os, sys, re
if not os.getcwd() in sys.path: # fix linux 软连接的 bug
    sys.path.append(os.getcwd())

import argparse
import struct

#from pythonx.funclib import *
#from pythonx.pelib import *
#from pythonx.mytoolspub import *
from common import *

forTONG = "forTONG" in sys.argv

_DOS_SIGNATURE         = b'MZ'
_PE_SIGNATURE          = b'PE\x00\x00'
_DOS_PE_OFFSET         = 0x3C   # offset of PE header pointer in DOS stub
_PE_OPT_HDR_OFFSET     = 24     # PE signature(4) + File Header(20)
_OPT_HDR_SUBSYS_OFFSET = 68     # offset of Subsystem field within Optional Header

IMAGE_SUBSYSTEM_WINDOWS_GUI = 2  # windowed application
IMAGE_SUBSYSTEM_WINDOWS_CUI = 3  # console application

def get_pe_subsystem(fpath):
    with open(fpath, 'rb') as f:
        if f.read(2) != _DOS_SIGNATURE:
            raise ValueError("not a valid PE file (missing MZ): {}".format(fpath))
        f.seek(_DOS_PE_OFFSET)
        pe_offset = struct.unpack('<I', f.read(4))[0]
        f.seek(pe_offset)
        if f.read(4) != _PE_SIGNATURE:
            raise ValueError("not a valid PE file (missing PE\\0\\0): {}".format(fpath))
        f.seek(pe_offset + _PE_OPT_HDR_OFFSET + _OPT_HDR_SUBSYS_OFFSET)
        return struct.unpack('<H', f.read(2))[0]

def is_gui_exe(fpath):
    return get_pe_subsystem(fpath) == IMAGE_SUBSYSTEM_WINDOWS_GUI

def is_console_exe(fpath):
    return get_pe_subsystem(fpath) == IMAGE_SUBSYSTEM_WINDOWS_CUI

def build_exe(keydir, winp=""):
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
def get_icon_cmd(exename, iconname, mcp=False):
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
    parser.add_argument('--entry', type=str, default='', help='entry exe name (without .exe)')
    args = parser.parse_args()
    return args

# kinstaller.exe -in kinstaller.exe -out loader20192.exe -mcp 65001 -debug 1
if __name__ == "__main__":

    args = parse_args()
    print(args.app, args.icon, args.mcp)

    if "pecopy" in sys.argv:
        build_exe("pecopy", getPlatform())
        # -mcp 65001 -- win10x64 不需要这玩意。
        cmdx = r"pecopy.exe -mcp 65001 -in pecopy.exe -out ..\..\dist\pecopy.exe -icon ..\image\icon\iconall\shitou.ico -mask ICONGROUP,MAINICON,0;ICONGROUP,107,2052;ICONGROUP,108,2052"
        print("***" * 30)
        print(cmdx)
        os.system(cmdx)

    elif "test" in sys.argv:
        build_exe("test", getPlatform())
        cmdx = r"test\test.exe -in test.exe -out test2.exe -mcp 65001 -debug 1"
        print("***" * 30)
        print(cmdx)
        os.system(cmdx)

    else:
        build_exe(args.app, getPlatform())
        cmdx = get_icon_cmd(args.app+r".exe", args.icon, args.mcp)
        print("***" * 30)
        print(cmdx)
        os.system(cmdx)
