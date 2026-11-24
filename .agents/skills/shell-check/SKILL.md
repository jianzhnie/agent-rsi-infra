---
name: shell-check
description: 检查 Shell 脚本语法（bash -n）并执行静态分析（shellcheck）。用法为 /shell-check [file_or_dir]；默认检查当前 Git 仓库中已跟踪及未跟踪且未被忽略的 .sh 文件。
license: Apache-2.0
metadata:
  version: 1.0.0
  author: Robin
  platforms: [linux, macos, windows]
  tags: [Check, Skill, Shell, Lint, Static-Analysis]
  related_skills: []
---

# Shell 检查

运行 [scripts/check.sh](scripts/check.sh)，不要临时重写文件收集与汇总逻辑：

```bash
bash <skill-directory>/scripts/check.sh [file-or-directory]
```

- 显式文件只检查该文件；目录递归检查 `.sh`。无参数时检查当前 Git 仓库中已跟踪及未跟踪、未忽略的 `.sh` 文件。
- 路径按调用目录解释；默认仓库模式从 Git 根运行。脚本使用 NUL 分隔，支持空格和换行文件名。
- 每项失败后继续。缺少 shellcheck 时仍执行语法检查，汇总为跳过并返回非零；没有选中脚本或目标无效时同样不报告通过。
- 根据实际输出报告文件数、失败和跳过项。检查通过不代表脚本运行行为已验证；行为变化还需相关回归测试。
