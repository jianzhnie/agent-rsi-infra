---
name: shell-style
description: 基于 Google Shell 风格指南，适配 Bash 4.2 及以上版本的 Shell 编码规范。
version: 1.0.0
author: Robin
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  tags: [Rule, Shell, Bash, Style, Formatting]
  related_skills: [shell-check]
paths:
  - "**/*.sh"
  - "**/*.bash"
---

# Shell 脚本规范

本项目所有 Shell 脚本必须遵循以下约定。基于 Google Shell 风格指南，适配 Bash 4.2 及以上版本。

## 目录

- [文件结构](#文件结构)
- [命名约定](#命名约定)
- [注释](#注释)
- [格式](#格式)
- [变量与常量](#变量与常量)
- [函数](#函数)
- [条件判断](#条件判断)
- [错误处理](#错误处理)
- [命令替换与管道](#命令替换与管道)
- [规模限制](#规模限制)
- [静态检查](#静态检查)
- [最佳实践](#最佳实践)

## 文件结构

脚本必须按以下顺序组织：

1. **解释器声明**和 `set` 选项。
2. **常量**与 `readonly` 导出。
3. **函数**：集中放置，函数之间不夹杂可执行代码。
4. **`main` 函数**：适用于至少包含一个其他函数的脚本。
5. **调用 `main`**：放在底部，使用 `main "$@"`。

```bash
#!/bin/bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly VERSION="1.0"

my_func() {
    ...
}

main() {
    my_func
}

main "$@"
```

规则：

- **解释器声明**：使用 `#!/bin/bash`，而非 `#!/usr/bin/env bash`，以兼容 Bash 4.2 及以上版本。
- **直接执行的脚本**必须以 `set -euo pipefail` 开始。
- **被加载的文件**（如 `common.sh`）不得设置 Shell 选项，应继承调用者的设置。
- **库文件**必须使用 `.sh` 后缀；可执行脚本可省略后缀。

## 命名约定

| 元素 | 约定 | 示例 |
|---------|-----------|---------|
| 脚本／文件 | `lower_snake_case` | `run_server.sh`、`common.sh` |
| 函数 | `lower_snake_case` | `run_server()`、`mylib::helper()` |
| 变量 | `lower_snake_case` | `local count`、`file_path` |
| 常量／`readonly` | `UPPER_SNAKE_CASE` | `readonly MAX_RETRIES=3` |
| 导出变量 | `UPPER_SNAKE_CASE` | `export PATH_TO_DATA` |
| 循环变量 | 与集合名称对应 | `for file in "${files[@]}"; do` |

规则：

- 使用 `readonly` 或 `declare -r` 显式声明常量。
- 函数内部变量使用 `local`。
- 关联变量使用一致的命名风格，如 `user_name`、`user_id`、`user_home`。

## 注释

### 文件头

每个可执行脚本必须有说明用途和用法的文件头注释：

```bash
#!/bin/bash
# run_server.sh — 启动推理服务器。
#
# 用法: run_server.sh [--port PORT] [--workers N]
# 选项：
#   --port     服务端口（默认 8000）
#   --workers  工作进程数（默认 4）
```

### 函数注释

函数头注释应说明用途、参数和返回值：

```bash
# 对指定端点执行健康检查。
# 参数：
#   $1: 端点 URL
#   $2: 超时秒数（默认 30）
# 返回值：
#   健康时返回 0，否则返回 1
health_check() {
    ...
}
```

### 行内注释

- 解释原因，具体实现由代码展示。
- 待办事项使用 `# TODO(username): 待办说明`。
- 使用 UTF-8 编码，说明性注释统一使用中文。

## 格式

- **缩进**：4 个空格，不使用制表符。
- **行长**：最多 120 个字符，使用反斜杠或分组换行。
- **行尾分号**：省略行尾的 `;`。
- **末尾逗号**：多行项目的最后一项添加逗号。

### 控制结构格式

```bash
# 正确：; do / ; then 与 for/if/while 位于同一行
for file in "${files[@]}"; do
    echo "$file"
done

if [[ -f "$config" ]]; then
    source "$config"
elif [[ -d "$config_dir" ]]; then
    source "${config_dir}/default.conf"
else
    echo "Config not found" >&2
    exit 1
fi

# 正确：case 格式
case "$action" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    *)
        echo "Unknown action: $action" >&2
        exit 1
        ;;
esac
```

规则：

- `; do` 和 `; then` 必须与 `for`／`if`／`while` 位于同一行。
- `else`、`fi`、`done` 各自独占一行。
- 同一脚本内不混用单行和多行 `if` 风格。

### 引号

- 包含变量、命令替换、空格或 Shell 元字符的字符串**始终加双引号**。
- 使用带花括号的变量形式以提高可读性。
- 整数字面量不加引号。
- 不含变量的命令选项和路径字面量不加引号。

```bash
# 正确
echo "Processing: ${file_name}"
cmd --max="${MAX_COUNT}"

# 错误：变量未加引号
echo $file_name

# 正确：整数字面量不加引号
exit 1
```

## 变量与常量

### 声明

```bash
# 正确：命令替换的声明和赋值分开
local file_count
file_count=$(wc -l < "$file")

# 正确：简单赋值可写在一行
local name="server"
readonly MAX_CONN=100

# 错误：命令替换与声明写在同一行
local file_count=$(wc -l < "$file")
```

### 默认值与替换

```bash
# 使用 :- 设置默认值
port="${SERVER_PORT:-8000}"
name="${1:?Error: server name is required}"
```

### 数组

- 列表使用数组，不使用字符串表示序列。
- 数组展开始终加引号。

```bash
local files=("config.json" "model.pt" "tokenizer.json")
for f in "${files[@]}"; do
    echo "$f"
done
```

### 特殊变量

- `$@` 和 `$*` 始终加引号：优先使用 `"$@"`，必要时使用 `"$*"`。
- 除非明确需要拼接，否则优先使用 `"$@"` 而非 `"$*"`。

## 函数

### 定义

```bash
# 正确
run_server() {
    ...
}

# 正确：库函数
mylib::helper() {
    ...
}
```

规则：

- 左花括号 `{` 与函数名位于同一行。
- 函数名与 `()` 之间不加空格。
- `function` 关键字可选；采用后应保持一致。

### 返回值

- 仅返回**退出状态**，0 表示成功，非零表示失败。
- 不使用 `return` 传递计算结果，改用 `echo` 或变量。

```bash
# 正确：返回退出状态
is_file_readable() {
    local file="$1"
    [[ -r "$file" ]]
}

# 正确：通过 echo 输出结果
get_file_size() {
    local file="$1"
    stat -c %s "$file"
}

# 错误：通过返回值传递计算结果
compute_sum() {
    local a="$1" b="$2"
    return $((a + b))  # 错误：return 接受 0 至 255 的退出码
}
```

### 局部变量

```bash
my_func() {
    local input_file="$1"
    local count=0
    ...
}
```

## 条件判断

| 推荐 | 避免 |
|-----------|-------|
| `[[ ... ]]` | `[ ... ]`, `test`, `/usr/bin/[` |
| `(( ... ))` 用于数值判断 | `let`、`$[ ... ]`、`expr` |
| `-z`、`-n` 用于空字符串判断 | 拼接额外字符判断空值 |
| `==` 用于字符串相等判断 | `=`，易与赋值混淆 |

```bash
# 正确
if [[ -z "$name" ]]; then
    echo "Name is empty"
fi

if (( retries > MAX_RETRIES )); then
    echo "Too many retries"
fi

# 正确：显式使用 -n / -z
if [[ -n "$value" ]]; then ... fi
if [[ -z "$value" ]]; then ... fi
```

## 错误处理

### 出错即退出

可执行脚本顶部始终使用 `set -euo pipefail`：

- `set -e`：命令失败时立即退出。
- `set -u`：引用未定义变量时退出。
- `set -o pipefail`：管道中任一命令失败，整个管道即失败。

### 错误信息

- 所有错误信息写入**标准错误输出**（`>&2`）。
- 使用辅助函数统一错误输出。

```bash
err() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

die() {
    err "$*"
    exit 1
}

# 用法
die "Failed to load config: ${config_file}"
```

### 检查结果

- 未使用 `set -e` 时，显式检查返回值。
- 未使用 `pipefail` 时，管道执行后立即读取 `PIPESTATUS`。

```bash
some_command
if [[ $? -ne 0 ]]; then
    die "Command failed"
fi
```

### 清理

使用 `trap` 在退出或出错时清理：

```bash
cleanup() {
    rm -f "${temp_file}"
}
trap cleanup EXIT
```

## 命令替换与管道

### 命令替换

- 始终使用 `$(command)`，不使用反引号。
- 声明和赋值分开，参见变量章节。

### 管道

- 优先使用内置命令。
- 避免将管道连接到 `while read`，改用进程替换。

```bash
# 错误：子 Shell 中的变量修改不会影响外层
ls | while read -r file; do
    count=$((count + 1))
done

# 正确：进程替换
while read -r file; do
    count=$((count + 1))
done < <(ls)
```

### 通配符

- 通配符始终附带显式路径：使用 `./*`，而非 `*`。

```bash
# 正确
rm -rf ./*

# 错误
rm -rf *
```

## 规模限制

- **脚本**：少于 400 行。
- **函数**：少于 50 行。
- 函数超过 50 行时，提取辅助函数。
- 脚本超过 400 行时，考虑拆分模块。

## 静态检查

- 所有代码必须通过 `shellcheck`。
- 仅允许 `disable=SC2086`，且必须附解释原因的注释。

```bash
# shellcheck disable=SC2086：此处有意进行单词拆分
rm -rf ${files_to_remove}
```

## 最佳实践

- **避免 `eval`**：存在安全风险，改用数组或函数。
- 脚本中**避免别名**，改用函数。
- **避免临时文件**：优先使用进程替换；确有需要时使用 `mktemp`。
- **避免魔法数字**：在顶部定义常量。
- **避免 `cat | grep`**：直接使用 `grep pattern file`。
- **幂等性**：脚本应可安全地多次运行。
- 环境变量赋值使用**绝对路径**；相对路径必须带 `./` 前缀。
- **脚本目录**：使用以下方式可靠定位：`SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"`
- **参数校验**：检查参数数量，或提供 `--help`／`usage`。

```bash
usage() {
    echo "Usage: $0 <config_file>"
    exit 1
}

[[ $# -eq 1 ]] || usage
```
