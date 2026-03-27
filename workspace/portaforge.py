#encoding=utf8
from gen_data import *
from gen_pkg import *


if __name__ == "__main__":
    args = parse_args()
    print(args.app, args.icon, args.mcp)
    
    # 首先制作打包数据
    gen_pack(args.app)

    print("ok")

