#!/bin/bash
# 补丁拒绝文件检查: 任何 .rej 残留 = 有补丁 hunk 未打上, 立即失败构建 (防静默缺补丁, 坑 8 类问题)
WS="${GITHUB_WORKSPACE}/kernel_workspace"
REJ=$(find "$WS" -name '*.rej' 2>/dev/null)
[ -z "$REJ" ] && { echo "patch reject 检查: 无 .rej 残留, OK"; exit 0; }
echo "::error::发现补丁拒绝文件(.rej)——以下补丁 hunk 未打上, 禁止继续编译:"
for f in $REJ; do
  echo "  ${f#$WS/} ($(grep -c '^@@ ' "$f" 2>/dev/null) 个失败 hunk)"
done
exit 1
