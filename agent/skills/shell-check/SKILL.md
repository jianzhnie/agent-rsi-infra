---
name: shell-check
description: 检查 Shell 脚本语法（bash -n）并执行静态分析（shellcheck）。用法为 /shell-check [file_or_dir]；默认检查当前 Git 仓库中已跟踪及未跟踪且未被忽略的 .sh 文件。
version: 1.0.0
author: Robin
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  tags: [Check, Skill, Shell, Lint, Static-Analysis]
  related_skills: [check]
---
对指定目标执行 Bash 语法检查和 shellcheck 静态分析。

## 用户提供文件路径时

对该文件运行两项检查：

```bash
bash -n "$TARGET" 2>&1
shellcheck "$TARGET" 2>&1
```

## 目录或默认仓库目标

使用 Bash 和以 NUL 分隔的文件名，正确处理空格及嵌套路径。
运行前检查是否安装 `shellcheck`；缺失时报告不可用，
仍执行 `bash -n`，不能将缺少工具报告为检查通过。

提供目录参数时，使用以下方式收集文件：

```bash
find "$TARGET" -type f -name '*.sh' -print0
```

未提供参数时，收集已跟踪及未跟踪、且未被忽略的 Shell 文件，仓库根目录由
`git rev-parse --show-toplevel` 确定。不在 Git 仓库中时，请用户指定目标目录。

```bash
git ls-files --cached --others --exclude-standard -z -- '*.sh'
```

使用 Bash 循环读取选定文件，对每个存在的文件执行
两项检查。单项失败后继续，并汇总结果：

```bash
while IFS= read -r -d '' file; do
    [[ -f "$file" ]] || continue
    bash -n "$file"
    shellcheck "$file"
done < <(find "$TARGET" -type f -name '*.sh' -print0)
```

上述循环仅展示执行方式，不代表检查结果。必须显式记录每条命令的
退出状态，不得因启用 `set -e` 而在首次失败时停止。
仓库模式从仓库根目录运行，并将 `find` 替换为
前面的 `git ls-files` 命令。文件来源可能重复时，
检查前先去重。

## 结果报告

逐文件报告：
- **语法检查**（`bash -n`）：通过（PASS）或失败（FAIL），失败时附解析错误详情。
- **静态分析**（`shellcheck`）：通过或无问题，或列出文件、行号、严重程度（错误／警告／提示）及问题说明。

最后汇总文件总数、语法通过及失败数量、静态分析无问题及有问题数量。
