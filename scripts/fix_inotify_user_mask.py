# -*- coding: utf-8 -*-
"""老基内核补 inotify_mark_user_mask (static inline, 移植自 GKI 新代际树, 如 mt6983 t_13.1+)。
背景: susfs fdinfo hunk 按新 GKI 上下文书写(调用 inotify_mark_user_mask), 老基(如 mt6983 t_13.0)
的 fs/notify/inotify/inotify.h 没有该函数 -> fdinfo.c implicit declaration 编译失败。
用法: python3 fix_inotify_user_mask.py [--header fs/notify/inotify/inotify.h]
已有该函数则为 no-op。"""
import os, sys

BLOCK = """
/* 移植自新代际 GKI 树(如 mt6983 t_13.1): susfs fdinfo hunk 依赖 */
#define INOTIFY_USER_MASK (IN_ALL_EVENTS | IN_ONESHOT | IN_EXCL_UNLINK)

static inline __u32 inotify_mark_user_mask(struct fsnotify_mark *fsn_mark)
{
\treturn fsn_mark->mask & INOTIFY_USER_MASK;
}
"""

def main():
    args = sys.argv[1:]
    hdr = args[args.index('--header') + 1] if '--header' in args else 'fs/notify/inotify/inotify.h'
    if not os.path.isfile(hdr):
        # 兼容老扁平布局
        alt = 'fs/notify/inotify_user.c'
        if os.path.isfile(alt):
            hdr = alt
        else:
            print(f'::error::找不到 inotify 头文件: {hdr} (cwd={os.getcwd()})')
            sys.exit(1)
    txt = open(hdr, encoding='utf-8', errors='ignore').read()
    if 'inotify_mark_user_mask' in txt:
        print(f'{hdr} 已含 inotify_mark_user_mask, no-op')
        return
    if not txt.endswith('\n'):
        txt += '\n'
    open(hdr, 'w', encoding='utf-8', newline='\n').write(txt + BLOCK.lstrip('\n') + '\n')
    print(f'已将 inotify_mark_user_mask (static inline) 追加到 {hdr}')

if __name__ == '__main__':
    main()
