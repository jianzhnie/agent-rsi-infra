---
name: git-conventions
description: 项目 Git 提交规范，包括 Conventional Commits 格式和提交规则。
version: 1.0.0
author: Robin
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  tags: [Rule, Git, Conventions, Commit]
  related_skills: []
---

# Git 提交规范

## 提交信息

使用 Conventional Commits 格式：

```
type(scope): description
```

类型： `feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`, `perf`

范围对应项目目录： `scripts`, `tools`, `docs`, `hooks`

## 提交规则

- 始终创建新提交；仅在用户明确要求时使用 `--amend`。
- 不跳过提交前钩子（`--no-verify`）。
- 不向 main/master 强制推送。
- 不提交可能包含密钥的文件，如 `.env`、`credentials.json`。

## 提交前钩子

除非用户明确要求，否则不修改 `.claude/settings.json` 或 `.claude/hooks/` 中已有的钩子配置。
