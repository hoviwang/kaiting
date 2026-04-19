---
name: 技能安装器
description: 读取包含安装说明的 URL，自动部署技能到 OpenClaw。当用户说「阅读(URL)并安装这个技能」，触发本技能，读取 URL 内容并执行安装步骤。
version: 1.0.0
author: user
tags: [automation, deployment, skill-management]
trigger: 阅读.*INSTALL|阅读.*install.*并安装|帮我安装.*技能|一键安装
---

# 技能安装器

## 触发方式

在 OpenClaw 中直接说（任意一种）：

```
阅读 https://github.com/hoviwang/kaiting/blob/main/INSTALL.md 并安装这个技能
安装 https://github.com/hoviwang/kaiting/raw/main/INSTALL.md
帮我安装这个技能 https://github.com/hoviwang/kaiting/raw/main/INSTALL.md
```

## 工作原理

1. 从用户消息中**提取 URL**（支持 GitHub raw / blob / raw.githubusercontent.com）
2. 用 `web_fetch` 读取 URL 内容
3. 从内容中解析出**安装命令**并执行
4. 报告安装结果

## 主 agent 执行步骤

### 步骤1：从消息中提取 URL

用正则从用户消息提取 INSTALL.md 的 raw URL：

```
GitHub blob URL → raw.githubusercontent.com URL
例: https://github.com/hoviwang/kaiting/blob/main/INSTALL.md
  → https://raw.githubusercontent.com/hoviwang/kaiting/main/INSTALL.md
```

### 步骤2：读取安装说明

用 `web_fetch` 工具读取 raw URL 内容：

```
web_fetch(url="<raw_url>")
```

### 步骤3：解析并执行安装命令

从 INSTALL.md 内容中提取 `bash` 代码块，作为 `exec` 命令执行。

典型安装命令格式：

```bash
mkdir -p ~/.openclaw/skills/<SkillName>.skill
git clone <repo_url> /tmp/<temp>
cp -r /tmp/<temp>/* ~/.openclaw/skills/<SkillName>.skill/
rm -rf /tmp/<temp>
```

### 步骤4：验证部署结果

```bash
ls ~/.openclaw/skills/<SkillName>.skill/
```

### 步骤5：报告结果

```
✅ 安装完成！

技能目录：~/.openclaw/skills/<SkillName>.skill/
文件列表：
  - SKILL.md
  - README.md
  - extract_context.py
  - references/...

重启 OpenClaw 后即可使用。
```

## 支持的 URL 格式

| 输入格式 | 自动转为 raw |
|---------|-------------|
| `https://github.com/user/repo/blob/main/INSTALL.md` | ✅ |
| `https://raw.githubusercontent.com/user/repo/main/INSTALL.md` | ✅ |
| `https://github.com/user/repo/raw/main/INSTALL.md` | ✅ |

## 错误处理

| 错误 | 处理方式 |
|------|---------|
| URL 无法解析 | 询问用户确认 URL 是否正确 |
| web_fetch 失败 | 尝试备用 URL 格式（blob → raw） |
| 安装命令执行失败 | 报告具体哪条命令失败 + 错误输出 |
| 目标目录已存在 | 询问「是否覆盖？」，用户确认后执行 |
| 非 .skill 格式文件 | 提示「这不是有效的 skill 安装文件」 |

## 示例对话

**用户**：
```
阅读 https://github.com/hoviwang/kaiting/blob/main/INSTALL.md 并安装这个技能
```

**主 agent**：
```
正在读取安装说明...
提取到 URL：https://raw.githubusercontent.com/hoviwang/kaiting/main/INSTALL.md
执行安装命令...
✅ 安装完成！
重启 OpenClaw 后，试试对我说「开庭」
```

## 注意事项

- 本技能本身需要先通过手动方式部署一次（见下方「初始部署」）
- 安装过程中如需输入密码或确认，会提示用户
- 仅支持 bash 命令安装（Linux/macOS/WSL）
- Windows 用户建议使用 WSL 或 Git Bash

---

## 初始部署（本技能本身）

手动复制一次，之后就能自我升级：

```bash
# 1. 创建目录
mkdir -p ~/.openclaw/skills/技能安装器.skill

# 2. 创建 SKILL.md（把本文件内容写入）

# 3. 重启 OpenClaw
openclaw restart
```

或通过任意文本编辑器创建 `~/.openclaw/skills/技能安装器.skill/SKILL.md`，粘贴本文件内容后重启。
