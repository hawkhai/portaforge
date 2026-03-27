#encoding=utf8
import os, sys, re
if not os.getcwd() in sys.path: # fix linux 软连接的 bug
    sys.path.append(os.getcwd())

import time

from pythonx.funclib import *
from pythonx.pelib import *
from pythonx.mytoolspub import *
from pythonx.filetool.pyinstxtractor import *
#from common import *

forTONG = "forTONG" in sys.argv

def get_file_time(fpath):
    if isPeFile(fpath):
        datestr = getPeFileStamp(fpath)
        # pyinstaller 生成的时间戳都一样，造成问题。
        datestr += int(getFileMd5(fpath)[:6], 16)
        while datestr > 0x7fffffff:
            datestr -= 0x100
        while datestr < 1628957195:
            datestr += 0x100
        # assert False, datestr
    elif True:
        datestr = 1628957195 # 315504000 # 1980-01-01 00:00:00
        datestr += int(getFileMd5(fpath)[:6], 16)
    else:
        frel = relativePath(fpath, ".")
        cmdx = 'git log -n 1 --pretty=format:"%at" --date=short -- "{}"'.format(frel) # "%ai" / at
        datestr = bytesToString(popenCmd(cmdx))
        if datestr:
            datestr = int(datestr)
            # assert False, datestr
        else:
            datestr = 1628957195 # 315504000 # 1980-01-01 00:00:00
            #assert False, datestr
    return formatTimeStamp(datestr)

# PECOPY RCDATA "pecopy/pecopy.exe"
def gen_pack(keydir, winp="", entry=""):
    pack = {}

    subdir = keydir
    if winp:
        subdir = keydir + "_" + winp

    baselibrary = "{}\\base_library.zip".format(subdir)
    if os.path.exists(baselibrary):
        rezipfile(baselibrary, ktouch=True)

    if entry:
        exename = entry
    else:
        exes = [f for f in os.listdir(subdir) if f.lower().endswith(".exe")]
        if len(exes) == 1:
            exename = exes[0][:-4]
        else:
            raise AssertionError(
                "entry exe is ambiguous, specify via entry= param (found: {})".format(exes)
            )

    mainexe = "{}\\{}.exe".format(subdir, exename)
    assert os.path.exists(mainexe), mainexe
    # 存在 bug，如果覆盖安装，文件更新了，又只判断了在不在，就必须这里修改一下。
    # 比如 msgbox 的 py 落地文件。
    # 理论上应该清理老的，不同版本混用，貌似存在 bug。
    """
Traceback (most recent call last):
  File "C:\Python\Python38\Lib\site-packages\PyInstaller\hooks\rthooks\pyi_rth_win32comgenpy.py", line 58, in <module>
  File "C:\Python\Python38\Lib\site-packages\PyInstaller\hooks\rthooks\pyi_rth_win32comgenpy.py", line 42, in _pyi_rthook
  File "PyInstaller\loader\pyimod02_importers.py", line 385, in exec_module
  File "win32com\__init__.py", line 5, in <module>
ImportError: DLL load failed while importing win32api: 找不到指定的模块。
[18880] Failed to execute script 'pyi_rth_win32comgenpy' due to unhandled exception!
    """
    version, sysversion = getPyhash() # getCurrentTimeStr(True)
    genrestime = round(time.time())

    def to_version_path(runfile):
        return runfile.replace("\\{}\\".format(version), "\\{version}\\", 1)

    rootdir = os.path.abspath(subdir)
    keynameset = set()
    runfileset = set()
    def process_file(fpath, fname, ftype):
        md5 = getFileMd5(fpath)
        fdata = readfile(fpath)
        relpathc = relativePath(fpath, rootdir).lower()
        assert relpathc not in pack.keys(), (relpathc, pack[relpathc])

        keyname = re.findall("[0-9a-zA-Z_]+", relpathc)
        while "_".join(keyname).upper() in keynameset:
            keyname.append(md5[:2])
        keyname = "_".join(keyname).upper()
        keynameset.add(keyname)

        zipfile = os.path.join("tempdir", keydir, keyname.lower(), md5[:16] + ".zip")

        newdate = get_file_time(fpath)
        modifyFileTime2(fpath, newdate)

        xtime = formatTimeStamp(getFileModifyTime(fpath))
        assert newdate == xtime, (xtime, newdate)
        copyfile(fpath, zipfile) # 创建文件夹。
        osremove(zipfile) # 如果存在，先移除。

        runfile = os.path.join(subdir, version, relpathc)
        runfileset.add(runfile)

        assert 0 == gzipfile(zipfile, to_version_path(runfile), fpath, ktouch=False)
        md5z = getFileMd5(zipfile)

        pack[relpathc] = {
            "md5": md5, # 原始文件的 MD5
            "md5z": md5z, # 压缩文件的 MD5
            "zipfile": zipfile, # zip 文件的地址。
            "keyname": keyname, # RC 里面的名字。
            "runfile": os.path.join("pyenv", to_version_path(runfile)),
            "fmtime": newdate,
            "fsize": os.path.getsize(fpath),
            "fzsize": os.path.getsize(zipfile),
            "petype": getPeType(fpath),
        }
        print(md5, md5z, zipfile, xtime)

    searchdir(rootdir, process_file)

    # 入口函数。
    zloader = "{}\\{}\\{}.exe".format(subdir, version, exename.lower())
    if not zloader in runfileset:
        for x in runfileset:
            print(x)
        assert False, zloader
    writepack = {
        "zloader": os.path.join("pyenv", to_version_path(zloader)),
        "files": pack,
        "version": version,
        "sysversion": sysversion,
        "genrestime": genrestime,
        "petype": getPeType(mainexe),
    }
    writefileJson(subdir+".json", writepack)
    # PECOPY RCDATA "pecopy/pecopy.exe"
    keys = [key for key in pack.keys()]
    keys.sort()
    lirc = []
    lirc.append("ZLOADER_ROOT_JSON RCDATA \"{}\"".format(subdir+".json"))
    for key in keys:
        keyname = pack[key]["keyname"]
        line = "{} RCDATA \"{}\"".format(keyname, pack[key]["zipfile"].replace("\\", "\\\\"))
        lirc.append(line)
    fdata = "\r\n".join(lirc)
    writefile(subdir+".rc", fdata)

def scan_checksums(keydir, winp=""):
    subdir = keydir
    if winp:
        subdir = keydir + "_" + winp

    retli = {}
    def process_file(fpath, fname, ftype):
        retli[fpath] = getFileMd5(fpath)
    searchdir(keydir, process_file)
    writefileJson(subdir+".json", retli)
    return subdir+".json"

def check_extracted(keydir, winp=""):
    subdir = keydir
    if winp:
        subdir = keydir + "_" + winp

    exefile = "{}/{}.exe".format(subdir, keydir)
    if not os.path.exists(exefile):
        print(exefile)
        return False

    cleardir("{}.exe_extracted".format(keydir))
    assert pyinstxtractorfile(exefile)
    jsonfile = scan_checksums("{}.exe_extracted".format(keydir), winp=winp)
    return True

if __name__ == "__main__":

    if "test" in sys.argv:
        gen_pack("test")

    if forTONG: # 文件夹
        gen_pack("forTONG", entry="forTONG_relv5")

    for arg in sys.argv:
        if check_extracted(arg, getPlatform()):
            print(arg)
            gen_pack(arg, getPlatform())
    print("ok")
