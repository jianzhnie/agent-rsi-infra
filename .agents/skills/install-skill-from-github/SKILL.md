---
name: install-skill-from-github
description: 从 GitHub 仓库目录或 SKILL.md 链接迁入完整 Agent Skill，保留资源、许可与来源记录。用于安装外部技能到本仓库或显式指定目录，不用于安装 Python 包或执行刚下载的代码。
license: Apache-2.0
---

# 从 GitHub 安装 Skill

使用 [scripts/install-skill-from-github.py](scripts/install-skill-from-github.py)。默认目标是脚本所属的共享技能目录，即本仓库 `.agents/skills/`；不写入用户的 `~/.codex/skills`。

## 输入与运行

接受仓库与路径，或 GitHub `tree` / `blob/.../SKILL.md` 链接：

```bash
python3 <skill-directory>/scripts/install-skill-from-github.py \
  --repo owner/repository --path path/to/skill --ref <commit-or-ref>

python3 <skill-directory>/scripts/install-skill-from-github.py \
  --url https://github.com/owner/repository/blob/main/path/to/skill/SKILL.md
```

优先固定用户指定版本；需要可复现快照时使用完整 commit SHA。分支名含 `/` 时，使用 `--repo`、`--path`、`--ref` 分别传参，避免 URL 的分支与路径边界歧义。

- `--path` 可传多个目录，或以 `SKILL.md` 结尾的路径；仓库根技能使用 `--path SKILL.md --name <skill-name>`。
- `--dest` 显式指定其他技能集合目录；相对目标路径按调用目录解释。
- `--name` 仅用于单个技能，不改写其 Frontmatter；需要改名时同步核对发现名称，不能假装原文未变。
- `--method auto|download|git`：默认先下载 ZIP，401/403/404 时尝试 Git HTTPS/SSH。私有下载读取 `GITHUB_TOKEN` 或 `GH_TOKEN`，Git 使用已有凭证；不要输出凭证。

## 安装边界

先检查上游技能内容、附属文件、许可和工具依赖。安装会复制完整技能目录（不复制 `.git`），不会安装第三方工具、启用 Hooks、改写权限或执行下载的脚本。

目标已存在（含失效链接）、路径越界、目录链接或指向技能外的文件链接均拒绝。批量任务先验证所有来源，再写入；失败时回滚本次创建的技能目录，不覆盖原有内容。

如果技能没有自带许可，脚本尝试保留仓库根的 `LICENSE`、`LICENSE.txt` 或 `COPYING`，并保留根 `NOTICE`。额外许可或技能外引用需人工检查，不能把自动复制当作完整许可审查。

每个技能生成 `INSTALL_SOURCE.json`，记录仓库、路径、请求版本与可确认的 commit。下载可变分支时 `resolved_commit` 可能为 `null`，不得将其描述为固定快照。来源自带同名文件时停止，避免覆盖其元数据。

## 完成迁入

检查相对引用、元数据和真实依赖，更新本仓库 README 与 Claude 资源索引，再运行相关检查。保持上游原文或记录本地适配，不自动迁入无关技能或整套仓库规则。

报告安装位置、版本、改动和未验证范围。下轮可发现新技能；实际客户端加载按其发现与显式调用策略确认。
