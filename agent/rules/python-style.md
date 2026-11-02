---
name: python-style
description: 基于 Google Python 风格指南，适用于 Python 3.10 及以上版本的编码规范。
version: 1.0.0
author: Robin
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  tags: [Rule, Python, Style, Formatting]
  related_skills: [check]
paths:
  - "**/*.py"
  - "**/*.pyi"
---

# Python 编码规范

基于 [Google Python 风格指南](https://google.github.io/styleguide/pyguide.html)，适配 Python 3.10 及以上版本。

推荐工具：ruff、black（88 字符、双引号）、isort、mypy。

---

## 1 模块组织

### `__all__`（推荐）

建议公共模块显式导出 `__all__` 列表，作为公共 API 的唯一依据。此项不是硬性要求：项目不使用通配符导入，缺少 `__all__` 不影响功能。

```python
__all__ = ["UserService", "create_user", "UserError"]
```

### `from __future__ import annotations`（可选）

支持 PEP 604（`X | Y`）及注解延迟求值。本项目面向 Python 3.10 及以上版本，无需此导入也可使用 `X | Y`。

**若代码使用以下功能，应跳过此导入**：`torch.jit.script`、运行时 `typing.get_type_hints()`，或数据类中的 `ClassVar`／`InitVar`。延迟字符串注解可能破坏这些功能，其他场景可安全使用。

### 主入口保护

所有可执行脚本都应定义并调用 `main()` 函数：

```python
def main() -> None:
    ...

if __name__ == "__main__":
    main()
```

### 导入顺序

按以下顺序分组，组内按字母排序，组间空一行：

1. `from __future__ import ...`（如有）
2. 标准库
3. 第三方库
4. 项目自身或本地模块

规则：
- 包使用 `import x`；使用 `from x import y` 时，`x` 为包前缀。
- 仅对广泛认可的缩写使用 `import y as z`，如 `np`、`pd`。
- 不使用相对导入、通配符导入或一行多个导入。

```python
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import ClassVar, Final, TypeAlias

import numpy as np
import pandas as pd

from myproject.core import Config
from myproject.utils import helper
```

抽象基类优先从 `collections.abc` 导入，例如使用 `from collections.abc import Iterator`，而非 `from typing import Iterator`。

---

## 2 格式

**行长**：最多 88 个字符。使用 `()`、`[]`、`{}` 内的隐式续行，不使用反斜杠续行。

**缩进**：4 个空格，不使用制表符。

**空行**：顶层类和函数定义之间空两行，方法定义之间空一行，导入组之间空一行。

**空白**：`()`、`[]`、`{}` 内侧不加空格；逗号、冒号、分号后空一格；二元运算符两侧空一格。关键字参数中的等号两侧不加空格，如 `func(a=1)`；带类型注解的默认值等号两侧空一格，如 `def func(a: int = 1)`。

**末尾逗号**：右括号独占一行时，最后一项必须加逗号：

```python
my_list = [
    1,
    2,
    3,
]
```

## 3 命名

| 类型 | 约定 | 示例 |
|------|------------|---------|
| 模块／包 | `lower_snake_case` | `my_module` |
| 类／异常／类型别名 | `CapWords` | `MyClass`、`ValueError`、`ProcessorConfig` |
| 函数／方法／变量 | `lower_snake_case` | `my_function`、`block_size` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_SIZE` |
| 私有或内部成员 | 下划线前缀 | `_internal_func` |

禁止：
- 使用连字符、携带类型信息的名称（如 `id_to_name_dict`）、保留的双下划线名称，以及紧凑循环之外的单字符名称（如 `i`、`j`、`k`）。

---

## 4 类型注解

### 必需注解

所有公共函数和方法必须为参数及返回值添加类型注解。

### 现代语法（3.10 及以上版本）

- 使用 `X | Y` 替代 `Union[X, Y]`。
- 使用 `X | None` 替代 `Optional[X]`。
- 使用内置泛型：`list[int]`、`dict[str, int]`、`tuple[int, str]`。

### 特殊类型

| 类型 | 用途 |
|------|------|
| `ClassVar` | 类级可变属性 |
| `TypeAlias` | 模块级复杂类型的简写 |
| `Final` | 不应重新赋值的常量 |
| `Any` | 仅用于确实无法表达类型的情况 |

### None 默认值

显式使用 `None` 默认值时，类型中必须包含 `| None`：

```python
def func(a: str | None = None) -> None:  # 正确
    ...
```
```python
def func(a: str = None) -> None:          # 错误
    ...
```

### 规则

- `self` 和 `cls` 无需注解。
- `__init__` 返回类型无需注解。
- 抽象类型优先使用 `collections.abc` 中的 `Sequence`、`Mapping`、`Iterable`，而非 `typing` 中的对应类型。

---

## 5 文档字符串

始终使用三个双引号，公共 API 遵循以下结构。

### 模块

```python
"""用一句话概述模块。

空一行，再补充模块的详细说明。
"""
```

### 函数／方法

```python
def my_function(arg1: int, arg2: str) -> bool:
    """用一句话概述，不超过 88 个字符，以句号结尾。

    Args:
        arg1: 参数 arg1 的说明。
        arg2: 参数 arg2 的说明。

    Returns:
        返回值说明。

    Raises:
        ValueError: 参数 arg1 为负数时。
    """
```

规则：
- 摘要占一行，以句号、问号或感叹号结尾。
- 公共 API 使用 `Args`、`Returns`、`Raises` 小节。
- 私有方法（下划线前缀）可使用单行文档字符串或省略。
- 不解释显而易见的内容。

### 类

```python
class MyClass:
    """用一句话概述。

    Attributes:
        attr1: 属性 attr1 的说明。
        attr2: 属性 attr2 的说明。
    """
```

---

## 6 注释

- 解释原因和意图。
- 块注释放在相关代码上方，不放在行尾。
- 提交前删除已注释掉的代码。
- 不在代码注释中引用 PR 编号或工单 ID。

待办注释格式：

```python
# TODO(username): 待完成的事项。
```

---

## 7 错误处理

- 捕获最具体的异常；除非立即重新抛出，否则不使用裸 `except:` 或 `except Exception:`。
- 不静默吞掉异常，至少记录日志。
- 自定义异常必须继承已有异常，名称以 `Error` 结尾。
- 使用 `raise from` 保留异常堆栈：

```python
try:
    data = load_file(path)
except FileNotFoundError as e:
    raise RuntimeError(f"Failed to load {path}") from e
```

- 文件和资源使用 `with`，清理操作使用 `finally`。
- 缩小 `try` 范围，仅包含可能失败的语句。

### 断言（assert）

`assert` 仅用于内部不变条件，即不可恢复的逻辑错误；不用于输入校验或运行时检查，因为 `-O` 可禁用断言。

```python
# 正确：内部不变条件
assert x >= 0, "internal: negative value after normalization"

# 错误：运行时检查
assert os.path.exists(path), "Path must exist"
```

---

## 8 值与比较

### 布尔判断

| 推荐 | 避免 |
|--------|-------|
| `if seq:` | `if len(seq) != 0:` |
| `if not seq:` | `if len(seq) == 0:` |
| `if val is None:` | `if val == None:` |
| `if flag:` | `if flag == True:` |
| `if not flag:` | `if flag == False:` |

当 `0` 是有效值时，应显式比较：使用 `if x == 0:`，而非 `if not x:`。

使用 `isinstance` 检查类型，如 `isinstance(x, MyClass)`，而非 `type(x) is MyClass`。

### 默认参数

不使用可变对象作为默认值：

```python
def foo(a, b: list[int] | None = None):
    if b is None:
        b = []
```
```python
def foo(a, b: Sequence[int] = ()):  # 同样有效：不可变元组
    ...
```

### 字符串格式化

- 行内格式化优先使用 f 字符串。
- 不在循环中使用 `+` 或 `+=` 累积字符串，使用字符串连接方法或 `io.StringIO`。
- 日志使用 `%` 风格占位符以延迟求值：

```python
logger.info("Loading from %s", path)     # 正确
logger.info(f"Loading from {path}")       # 错误：立即求值
```

模块级日志对象模式：

```python
import logging

logger = logging.getLogger(__name__)
```

---

## 9 常用模式

### 推导式与生成器

适用于简单场景，不使用多个 `for` 子句：

```python
result = [x * 2 for x in data if x > 0]     # 正确
has_positive = any(x > 0 for x in data)      # 正确：生成器，避免创建列表
has_positive = any([x > 0 for x in data])    # 错误 — unnecessary list
```

### 数据类

数据容器优先使用 `@dataclass`，通过 `__post_init__` 在字段初始化后执行校验：

```python
@dataclass
class Config:
    name: str
    max_items: int = 100

    def __post_init__(self) -> None:
        if self.max_items < 1:
            raise ValueError(f"max_items must be >= 1, got {self.max_items}")
```

### 枚举

使用 `Enum` 和 `auto()` 定义枚举：

```python
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETED = auto()
```

### 属性

使用 `@property` 替代属性读取和设置方法：

```python
@property
def full_name(self) -> str:
    return f"{self.first} {self.last}"
```

### 模式匹配（3.10 及以上版本）

枚举、数据类或元组的复杂分支优先使用模式匹配，避免冗长的 `if`／`elif` 链。

### 匿名函数

仅用于排序键等简单单行逻辑，多行逻辑使用嵌套 `def`。

### 上下文管理器

需要清理的资源均使用 `with`。简单上下文管理器优先使用 `@contextmanager`，有状态的使用 `__enter__`／`__exit__`。

### 类的约定

- 实例属性在 `__init__` 中初始化，不在之后动态添加。
- 避免使用 `staticmethod`，改用模块级函数。
- `classmethod` 仅用于具名构造器或类级状态。
- 仅在兼容 Python 2 时显式继承 `object`。

---

## 10 通用约定

- 文件操作优先使用 `pathlib.Path`，而非 `os.path`。
- 诊断信息使用 `logging`，不使用 `print()`。
- 函数职责应集中，超过约 40 行时考虑拆分。
- 与同一文件中的现有代码保持一致。
