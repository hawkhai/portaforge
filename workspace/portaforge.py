#encoding=utf8
from gen_data import *
from gen_pkg import *

# python3 portaforge.py --app samples\forTONG --icon icons\juice.ico
if __name__ == "__main__":
    args = parse_args()
    print(args.app, args.icon, args.mcp)
    
    # 首先制作打包数据
    mainexe = gen_pack(args.app, entry=args.entry)

    isgui = is_gui_exe(mainexe)
    build_exe(args.app, getPlatform(), isgui=isgui, mainexe=mainexe)
    cmdx = get_icon_cmd(args.app+r".exe", args.icon, args.mcp, isgui=isgui)
    print("***" * 30)
    print(cmdx)
    os.system(cmdx)

    print("ok")
