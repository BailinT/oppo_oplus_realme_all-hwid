# 欧加真全版本内核快速构建 · HWID 校验版（5.10 / 5.15 / 6.1 / 6.6 / 6.12）

OPPO/一加/真我 GKI 内核自动化编译 + **HWID 白名单校验**。
基于 `BailinT/oppo_oplus_realme_all`（非 hwid 大仓，35 个 workflow 全绿），只允许 `hwid/allowlist.txt` 中的设备启动。

## 与 `oppo_oplus_realme_all` 的差异

1. **Checkout 步骤**：首个 step 拉取本仓（私有资源本地 cp，不再 wget 自身）
2. **HWID 注入步骤**：初始化源码后注入 `hwid_lock.c` + `hwid_allowlist.h`（35 棵树锚点全部实测存在）
3. **CCACHE_KEY 加 `-hwid` 后缀**：缓存与非 hwid 仓互不干扰
4. 其余完全一致（含 5.10 的 LTO/CFI 修复、三仓合并的全部资源）

## HWID 机制（5-key 增强版）

读取 `androidboot.chipid` → `androidboot.cpuid` → `androidboot.emmcid` → `androidboot.serialno` → `oplusboot.serialno`，
**逐 key 全比对**，任一 key 命中 allowlist 即放行（`hwid_match` 先 strcasecmp 精确比对，再尝试 kstrtoull 数值比对）。
不在白名单 / 读不到任何 key → `panic()` 1 秒后重启。

当前 allowlist：**23 个设备 ID**（合并自 sm8650/sm8750/sm8850-hwid + 5x-hwid 四仓）。

## 支持的内核版本（35 个 workflow）

| 系列 | x |
|---|---|
| 5.10 | 66 / 110 / 149 / 168 / 198 / 209 / 226 / 236 |
| 5.15 | 74 / 123 / 167 / 180 |
| 6.1 | 57 / 75 / 115 / 118 / 128 / 134 / 141 / 157 |
| 6.6 | 30 / 50 / 56 / 57 / 66 / 89 / 118（含 `_mtk` 变体） |
| 6.12 | 23 / 38 / 58（含 `_gki` / `_mtk` 变体） |

## 加设备流程

1. 设备端（原厂内核）跑 `sh hwid/probe_hwid.sh [预期id]` → `/sdcard/hwid_probe.log`
2. 取**原始值**（不要信识别脚本格式化输出），确认来源 key
3. 填 `hwid/allowlist.txt`（`^[0-9a-z._:-]{4,128}$`，超长 ID 如小米 cpuid 必须原值逐字符一致）
4. 提交推送 → 触发构建 → **刷入前确认设备在 allowlist**（不在会 panic 不开机）

## 状态

- [x] 35 个 workflow 合并改造（Checkout + HWID 注入 + 资源本地化 + 缓存隔离）
- [x] 35 棵树注入锚点实测（6.6 树的 main.c 结构差异已确认兼容）
- [x] allowlist 合并 23 个设备 ID
- [ ] 首次构建验证

## 与 cctv18 三仓的差异（继承自非 hwid 大仓）

1. 5.x 的 SUSFS 源不同：cctv18 的 susfs4oki 无 5.x 分支，改用 ShirkNeko/susfs4ksu
2. 5.x 新增 vendor-fix 步骤（cctv18 在自家源码仓里预先修好）
3. 5.x 不支持 Droidspaces（ntsync 为 6.6+ 特性）
4. 5.10 的 LTO/CFI 修复：5.10 树 `HAS_LTO_CLANG` 依赖 `LLVM_IAS=1`，已加并强制 ThinLTO（对齐 Action-Build 产物形态）
