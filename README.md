# portaforge
Windows 绿色软件工厂。Windows Green Software Factory

# 基本原理

launcher 是一个启动器。
把散文件压缩打包到 launcher.exe 文件尾部。
运行的时候解压，然后转调用。

# 步骤

1. 把散文件整理到一个目录
2. 运行 gen_res.exe 把散文件预处理
3. 运行 gen_pkg.exe 把文件打包到 launcher.exe

