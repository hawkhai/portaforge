#encoding=utf8
import re, os, sys
import traceback
import platform

def getSystem():
    return platform.system() # Windows

def isWindows():
    return getSystem() == 'Windows'

def isLinux():
    return getSystem() == 'Linux'

def isMacOS():
    return getSystem() == 'Darwin'

def getArchitecture():
    # ('64bit', '') -- macOS
    # ('32bit', 'WindowsPE')
    return platform.architecture()

def isPython32():
    return getArchitecture()[0] == "32bit"

def isPython64():
    return getArchitecture()[0] == "64bit"

def getPlatform(debug=False):
    # win8x32
    # win10x64
    if isWindows():
        return "win{}x{}".format(platform.version().split(".")[0],
                                 platform.architecture()[0].split("bit")[0])
    return "{}{}x{}".format(platform.system(),
                            platform.version().split(".")[0],
                            platform.architecture()[0].split("bit")[0])

def getPyhash(debug=False):
    def myhash(data):
        import hashlib
        md5 = hashlib.md5()
        md5.update(data.encode('utf-8'))
        return md5.hexdigest()
    if debug:
        # 3.10.5 (tags/v3.10.5:f377153, Jun 6 2022, 16:14:13) [MSC v.1929 64 bit (AMD64)]
        # 3.8.1 (tags/v3.8.1:1b293b6, Dec 18 2019, 23:11:46) [MSC v.1916 64 bit (AMD64)]
        print(sys.version)
    # WindowsPE_64bit_10.0.17763_3.8.1_5.13.0_e60c469
    return "_".join([*platform.architecture()[::-1],
                     platform.version(),
                     platform.python_version(),
                     get_pyinstaller_version(),
                     myhash(sys.version)[:7]]), sys.version

def get_pyinstaller_version():
    import PyInstaller.__main__
    return PyInstaller.__main__.__version__

if __name__ == "__main__":
    print("PyInstaller version:", get_pyinstaller_version())

IS_WINDOWS = isWindows()
IS_LINUX = isLinux()
IS_MACOS = isMacOS()
IS_PY32 = isPython32()
IS_PY64 = isPython64()

def getAppdataLocalPrograms(subdir = "Python"):
    # 根据操作系统类型确定路径前缀
    if IS_WINDOWS:
        appdata_local_programs = os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', subdir)
    else:
        appdata_local_programs = 'N/A'  # 非Windows系统不具有AppData目录
        assert False, appdata_local_programs
    return appdata_local_programs

if __name__ == "__main__":
    print(getPyhash(True))
    print(getPlatform())
    print(getAppdataLocalPrograms())
