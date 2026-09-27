#!/bin/bash
# 补丁拒绝文件检查 v2: 任何 .rej 残留 = 有补丁 hunk 未打上; 白名单 = 按树尽力而为的已知良性项
WS="${GITHUB_WORKSPACE}/kernel_workspace"
REJ=$(find "$WS" -name '*.rej' 2>/dev/null)
[ -z "$REJ" ] && { echo "patch reject 检查: 无 .rej 残留, OK"; exit 0; }
# 白名单: unicode_bypass 按树 fs/unicode 版本兼容性尽力而为, 失配 hunk 为已知良性
BENIGN_FILTER='fs/unicode/.*\.rej$'
BAD=""
for f in $REJ; do
  echo "$f" | grep -qE "$BENIGN_FILTER" || BAD="$BAD $f"
done
[ -z "$BAD" ] && { echo "patch reject 检查: 仅 fs/unicode 良性失配(unicode_bypass 按树尽力而为), 放行"; exit 0; }
echo "::error::发现补丁拒绝文件(.rej)——以下补丁 hunk 未打上, 禁止继续编译:"
for f in $BAD; do
  echo "  ${f#$WS/} ($(grep -c '^@@ ' "$f" 2>/dev/null) 个失败 hunk)"
done
exit 1
