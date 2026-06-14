#encoding=utf8
from gen_data import *
from gen_pkg import *
from gen_nsis import build_nsis

# python3 portaforge.py --app samples\forTONG --icon icons\juice.ico
if __name__ == "__main__":
    args = parse_args()
    print(args.app, args.icon, args.mcp, args.installer)

    if args.installer != "embedded":
        outfile = build_nsis(
            args.app, args.icon, entry=args.entry, outdir=args.outdir,
            nsis=args.nsis, app_name=args.name, publisher=args.publisher,
            version=args.version, msi=args.installer == "msi",
            language=args.language)
        print(outfile)
        print("ok")
        raise SystemExit(0)

    # 首先制作打包数据
    mainexe = gen_pack(args.app, entry=args.entry)

    isgui = is_gui_exe(mainexe)
    build_exe(args.app, getPlatform(), isgui=isgui, mainexe=mainexe)
    cmdx = get_icon_cmd(args.app+r".exe", args.icon, args.mcp, isgui=isgui)
    print("***" * 30)
    print(cmdx)
    os.system(cmdx)

    print("ok")
