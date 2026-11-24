# 来源与本地改动

脚本来自 OpenAI 内置 `skill-installer` 的本机快照（2026-11-24），项目来源：https://github.com/openai/skills/tree/main/skills/.system/skill-installer 。未将可变的公开分支声称为本机快照的精确 commit。

保留原项目 [Apache-2.0 LICENSE](LICENSE)。两个脚本的文件头标明已修改；原始内容校验值：

- `install-skill-from-github.py` 原始 SHA-256：`38f311b75664bb063808f982c600271ebc4b560830f491705190f88a94e3e781`。
- `github_utils.py` 原始 SHA-256：`61c1bbe2ae217433b4b6f9f09f21aca4df52c12598068343ade719f706e4859b`。

本地扩展：

- 默认安装到当前 Skill 集合目录，支持 `SKILL.md` 文件链接和百分号编码路径。
- Git 回退补充指定 commit 的 fetch；不交互请求凭证，并限制网络和 Git 等待时间。
- 批量预检、互斥参数、目标拒绝覆盖与失败回滚；保留原有路径、ZIP 与链接校验。
- 安装时附带可取得的根许可、NOTICE 及 `INSTALL_SOURCE.json`，不执行技能代码。
- 保留原 `github_utils.py` 的认证来源；补充 HTTP 超时。

不改写系统的技能安装器，不修改用户的 Codex 全局技能目录。
