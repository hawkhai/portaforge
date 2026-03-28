# portaforge

Windows 绿色软件工厂。Windows Green Software Factory

# 基本原理

launcher 是一个启动器。
把散文件压缩打包到 launcher.exe 文件尾部。
运行的时候解压，然后转调用。

# 使用指南

1. 把散文件整理到一个目录
2. 运行 portaforge.exe

```bat
F:
cd F:\pythonx\portaforge\workspace
# python3 portaforge.py --app samples\forTONG --icon icons\juice.ico
dist\portaforge.exe --app samples\forTONG --icon icons\juice.ico
```

## 发布版本

portaforge.exe 自己就是用 portaforge.py 打包的。

```bat
F:
cd F:\pythonx\portaforge\workspace
set PATH=%PATH%;E:\kSource\pythonx\decode\pyenv\Python37\Scripts

pyinstaller --clean --noconfirm portaforge.py --distpath samples --exclude numpy --exclude PyQt5 --exclude selenium 

python3 portaforge.py --app samples\portaforge --icon icons\juice.ico

```

## 和 pyinstaller 单包的比较

1. 不用每次都解压，更快。
2. pyinstaller 如果崩溃会残留。
3. 可以支持任意散文件小软件。
