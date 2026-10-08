# -*- coding: utf-8 -*-
"""老世代 ace 系树补 bool scan_adjusted 声明(OEM 同步失误, 11r 树有)。
条件幂等: 已有则 no-op。"""
import sys

p = 'mm/vmscan.c'
try:
    txt = open(p, encoding='utf-8', errors='ignore').read()
except FileNotFoundError:
    print('::error::mm/vmscan.c 不存在 (cwd=%s)' % __import__('os').getcwd())
    sys.exit(1)

if 'bool scan_adjusted;' in txt:
    print('scan_adjusted 声明已存在, no-op')
    sys.exit(0)
if 'scan_adjusted' not in txt:
    print('vmscan 无 scan_adjusted 使用, no-op')
    sys.exit(0)

anchor = 'bool proportional_reclaim;'
replacement = 'bool proportional_reclaim;' + chr(10) + chr(9) + 'bool scan_adjusted;'
new = txt.replace(anchor, replacement, 1)
if new == txt:
    print('::error::proportional_reclaim 锚点未找到')
    sys.exit(1)
open(p, 'w', encoding='utf-8', newline='').write(new)
print('已补 bool scan_adjusted 声明')
