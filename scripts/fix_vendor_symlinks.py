# -*- coding: utf-8 -*-
"""通用 vendor 死链修复器 v2: 遍历内核树内悬空符号链接, 从 modules 仓补源。
用法: python3 fix_vendor_symlinks.py --tree common --modules modules
v2 行为(按 sm8475 单仓 12.1 实测迭代):
  - vendor/ 悬空链接 → modules 仓补源(目录/文件), 硬依赖必须补上;
  - 树内非 vendor 死链(QC 老世代遗留, 如 dts/vendor、touchpanel 头链接):
    * 若其目标最终落在已补源的目录内 → 第二遍扫描时自然自洽;
    * 否则仅告警不阻断(209/226/236 生产包同款死链可正常编译);
  - Documentation/ 装饰链接: 告警不阻断;
  - 全部 vendor 硬依赖补不齐才 exit 1。
"""
import os, sys, shutil

def main():
    args = sys.argv[1:]
    def opt(name, default):
        return args[args.index(name) + 1] if name in args else default
    tree = os.path.abspath(opt('--tree', 'common'))
    modules = os.path.abspath(opt('--modules', 'modules'))
    allow_missing = [x.strip() for x in opt('--allow-missing', '').split(',') if x.strip()]
    for d, n in ((tree, 'tree'), (modules, 'modules')):
        if not os.path.isdir(d):
            print(f'::error::{n} 目录不存在: {d} (cwd={os.getcwd()})')
            sys.exit(1)
    print(f'内核树: {tree}\nmodules 仓: {modules}')
    fixed, vendor_missing, internal_skip = [], [], 0
    disabled = []
    ok_links = 0
    # 两遍: 第一遍补 vendor 源, 第二遍让树内链接指向新补的目录
    for pass_no in (1, 2):
        fixed_this = 0
        for root, dirs, files in os.walk(tree):
            for name in dirs + files:
                p = os.path.join(root, name)
                if not os.path.islink(p):
                    continue
                tgt = os.readlink(p)
                res = os.path.normpath(os.path.join(os.path.dirname(p), tgt))
                if os.path.lexists(res):
                    if pass_no == 1:
                        ok_links += 1
                    continue
                if os.path.relpath(p, tree).replace(os.sep, '/').startswith('Documentation/'):
                    if pass_no == 1:
                        internal_skip += 1
                        print(f'  [skip-doc] {p.replace(os.sep, "/")} -> {tgt} (Documentation 树装饰)')
                    continue
                if 'vendor/' in tgt:
                    rel = tgt[tgt.index('vendor/'):].rstrip('/')
                    src = os.path.join(modules, rel)
                    if os.path.isdir(src) and not os.path.islink(src):
                        os.unlink(p)
                        os.makedirs(os.path.dirname(p), exist_ok=True)
                        shutil.copytree(src, p, symlinks=True)
                        fixed.append(rel)
                        fixed_this += 1
                        continue
                    if os.path.isfile(src):
                        os.unlink(p)
                        shutil.copyfile(src, p)
                        fixed.append(rel)
                        fixed_this += 1
                        continue
                    if pass_no == 2:
                        relp = p.replace(os.sep, '/')
                        if any(relp.endswith(s) or (s + '/') in relp + '/' for s in allow_missing):
                            os.unlink(p)
                            parent = os.path.dirname(p)
                            name = os.path.basename(p)
                            mk = os.path.join(parent, 'Makefile')
                            if os.path.isfile(mk):
                                mk_src = open(mk, encoding='utf-8', errors='replace').read()
                                mk_lines = mk_src.splitlines()
                                mk_new = '\n'.join(('# disabled(unopensource vendor link): ' + ln) if (name + '/') in ln or ('/' + name) in ln else ln for ln in mk_lines)
                                if mk_new != mk_src:
                                    open(mk, 'w', encoding='utf-8', newline='').write(mk_new)
                            print(f'  [DISABLED] {relp} -> {tgt} (驱动源不开源, 已删链接并注释 Makefile 引用)')
                            disabled.append(relp)
                        else:
                            vendor_missing.append((relp, tgt))
                else:
                    # 树内非 vendor 死链: Documentation 装饰或老世代遗留
                    if pass_no == 1:
                        relp = p.replace(os.sep, '/')
                        tag = 'skip-doc' if relp.startswith('Documentation/') else 'skip-internal'
                        internal_skip += 1
                        print(f'  [{tag}] {relp} -> {tgt}')
        if pass_no == 1 and fixed_this == 0:
            break  # 第一遍没补任何源, 第二遍不会改善
    print(f'自洽链接: {ok_links} | 已补源: {len(fixed)} | 已禁用不可补源: {len(disabled)} | vendor硬依赖缺失: {len(vendor_missing)} | 树内死链豁免: {internal_skip}')
    for rel in fixed:
        print(f'  [fixed] {rel}')
    for p, tgt in vendor_missing:
        print(f'  [VENDOR-MISSING] {p} -> {tgt}')
    if vendor_missing:
        print(f'::error::仍有 {len(vendor_missing)} 个 vendor 硬依赖死链无法补源')
        sys.exit(1)
    print('vendor 死链修复完成')

if __name__ == '__main__':
    main()
