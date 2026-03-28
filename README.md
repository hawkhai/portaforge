# portaforge — Windows 绿色软件工厂 / Windows Green Software Factory

Windows 下把散文件目录打包成单个可执行文件的工具。

A tool that packs a directory of loose files into a single self-contained executable on Windows.

## 基本原理 / How It Works

launcher 是一个启动器，把散文件压缩后附加到 launcher.exe 文件尾部；运行时自动解压并转调用目标程序。

A launcher stub is used as the host executable. All loose files are compressed and appended to its tail. At runtime the launcher extracts them and delegates execution to the target program.

## 使用指南 / Quick Start

1. 把散文件整理到一个目录
2. 运行 portaforge.exe，指定应用目录和图标

1. Organize all loose files into a single directory.
2. Run `portaforge.exe` with the application directory and icon path.

```bat
F:
cd F:\pythonx\portaforge\workspace
rem python3 portaforge.py --app samples\forTONG --icon icons\juice.ico
dist\portaforge.exe --app samples\forTONG --icon icons\juice.ico
```

## 发布版本 / Building a Release

portaforge.exe 自身通过 portaforge.py 打包生成。

`portaforge.exe` is itself packaged using `portaforge.py`.

```bat
F:
cd F:\pythonx\portaforge\workspace
set PATH=%PATH%;E:\kSource\pythonx\decode\pyenv\Python37\Scripts

pyinstaller --clean --noconfirm portaforge.py --distpath samples --exclude numpy --exclude PyQt5 --exclude selenium

python3 portaforge.py --app samples\portaforge --icon icons\juice.ico
```

## 与 pyinstaller 单包模式的比较 / Comparison with PyInstaller One-File Mode

1. 不用每次都解压，启动更快。
2. pyinstaller 崩溃时不会残留临时文件。
3. 可以支持任意散文件小软件。

1. No repeated extraction on every launch — startup is faster.
2. No leftover temporary files when the process crashes.
3. Works with any collection of loose files, not just Python apps.
