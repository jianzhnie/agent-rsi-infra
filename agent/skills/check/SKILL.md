---
name: check
description: 提交前运行项目已配置的 pre-commit 检查，并报告失败原因和修复提示，等同于 pre-commit run --all-files。
version: 1.0.0
author: Robin
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  tags: [Check, Skill, Pre-commit, Lint, Quality]
  related_skills: [shell-check]
---
运行项目完整的 pre-commit 检查：

```bash
pre-commit run --all-files
```

使用 `/check` 作为提交前检查的统一入口，替代 `/precheck`。

用中文报告各钩子的实际结果：通过（PASS）、失败（FAIL）或跳过（SKIPPED）。全部适用检查通过后，报告“所有检查均已通过”。若有失败，列出受影响文件、具体问题和修复提示。若钩子修改了文件，应报告变更并重新检查，再判断是否成功。仅推荐与项目已配置钩子相关的修复工具，不假定检查中包含 shellcheck、black、isort 或 mypy。
