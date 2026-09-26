# -*- coding: utf-8 -*-
# 通用清障 v3: 扫描 obj-$(CONFIG_X) += dir/ 引用的缺失/残缺驱动目录, 一律建空 Makefile stub
# CWD 自适应: 从当前目录或 ./common 定位内核树; 处理悬空符号链接; 带诊断输出
import os, re

root = './common' if os.path.isdir('./common/drivers') else '.'
print('CWD:', os.getcwd(), '| 内核树基准:', root)

pat = re.compile(r'obj-(?:\$\(CONFIG_[A-Za-z0-9_]+\)|[ym])[ \t]*\+?=[ \t]*([A-Za-z0-9_./-]+)/')
stubbed, walked, hits = 0, 0, 0
for top in ('drivers', 'sound', 'techpack'):
    base = os.path.join(root, top)
    if not os.path.isdir(base):
        continue
    for dirpath, dirs, files in os.walk(base):
        if 'Makefile' not in files:
            continue
        walked += 1
        for line in open(os.path.join(dirpath, 'Makefile'), encoding='utf-8', errors='ignore'):
            m = pat.search(line)
            if not m:
                continue
            hits += 1
            d = m.group(1)
            full = os.path.join(dirpath, d)
            mf = os.path.join(full, 'Makefile')
            if os.path.exists(mf):
                continue
            if os.path.islink(full) and not os.path.isdir(full):
                os.unlink(full)
            os.makedirs(full, exist_ok=True)
            open(mf, 'w').write('# stub: source missing in public tree\n')
            stubbed += 1
            print('stub:', full)
print('Makefile walked:', walked, '| dir 引用:', hits, '| stub:', stubbed)
