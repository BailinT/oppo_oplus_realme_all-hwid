# -*- coding: utf-8 -*-
# SUS_MAP 手工移植 v3: susfs 补丁 task_mmu.c Hunk#6(show_smaps_rollup SUS_MAP 包裹)在
# sm8750/mt6991/新树上上下文失配打不上 -> 按 Case-4 现场手工包裹, 成功后移除对应 .rej
# v3: 判定只看 Case-4 位置(全局字符串会被 Hunk#2/#3 污染)
import os, re
root = './' if os.path.isdir('./fs/proc') else './common/'
p = root + 'fs/proc/task_mmu.c'
if not os.path.exists(p):
    print('skip: task_mmu.c not found at', p); raise SystemExit
src = open(p, encoding='utf-8', errors='ignore').read()
i = src.find('/* Case 4 above */')
if i < 0:
    print('WARN: Case-4 marker not found, .rej 保留待人工审查'); raise SystemExit
window = src[i:i+900]
if '#ifdef CONFIG_KSU_SUSFS_SUS_MAP' in window:
    print('Case-4 已包裹, skip')
    rej = root + 'fs/proc/task_mmu.c.rej'
    if os.path.exists(rej):
        os.remove(rej); print('removed', rej)
    raise SystemExit
m = re.search(r'(if \(vma->vm_end > last_vma_end\) \{\n)(\t+)(smap_gather_stats\(vma, &mss, last_vma_end\);\n\2last_vma_end = vma->vm_end;\n)(\t+\})', window)
if not m:
    print('WARN: Case-4 inner pattern not found, .rej 保留待人工审查'); raise SystemExit
T = m.group(2)
repl = (m.group(1)
    + '#ifdef CONFIG_KSU_SUSFS_SUS_MAP' + chr(10)
    + T + 'if (!vma->vm_file || !(SUSFS_IS_INODE_SUS_MAP(file_inode(vma->vm_file)))) {' + chr(10)
    + T + chr(9) + 'smap_gather_stats(vma, &mss, last_vma_end);' + chr(10)
    + T + chr(9) + 'last_vma_end = vma->vm_end;' + chr(10)
    + T + '}' + chr(10)
    + T + '#else' + chr(10)
    + m.group(3)
    + T + '#endif /* CONFIG_KSU_SUSFS_SUS_MAP */' + chr(10)
    + m.group(4))
src = src[:i] + window.replace(m.group(0), repl, 1) + src[i+900:]
open(p, 'w', encoding='utf-8', newline='').write(src)
print('SUS_MAP wrapper hand-ported into show_smaps_rollup (v3)')
rej = root + 'fs/proc/task_mmu.c.rej'
if os.path.exists(rej):
    os.remove(rej)
    print('removed', rej)
