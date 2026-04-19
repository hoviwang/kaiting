---
name: 安装开庭
description: 一键安装「开庭.skill」杠精评审技能到 OpenClaw。说「安装开庭」，自动从 GitHub 克隆并部署主 skill。
version: 1.0.0
author: user
tags: [automation, deployment]
trigger: 安装开庭|安装 kaiting|部署开庭|一键安装开庭
---

# 安装开庭 — 自举引导

## 触发词

当你说「**安装开庭**」，本 skill 会自动部署「开庭」主 skill。

## 完整自举流程

### 只需做一次（手动）

把本 skill 复制到 OpenClaw skills 目录：

```bash
mkdir -p ~/.openclaw/skills/安装开庭.skill
cp ~/.openclaw/skills/开庭.skill/INSTALL.md ~/.openclaw/skills/安装开庭.skill/SKILL.md
```

（如果你从 GitHub 下载的仓库，解压后路径是 `/path/to/kaiting/INSTALL.md`）

重启 OpenClaw：`openclaw restart`

### 之后每次（自动）

对 OpenClaw 说：

```
安装开庭
```

就会自动执行：
1. `git clone https://github.com/hoviwang/kaiting.git /tmp/kaiting-main`
2. `cp -r /tmp/kaiting-main ~/.openclaw/skills/开庭.skill`
3. 验证文件完整性
4. 清理临时文件

---

## 文件结构（部署后）

```
~/.openclaw/skills/开庭.skill/
├── SKILL.md
├── README.md
├── extract_context.py
└── references/
    └── subagent-prompt.md
```

## GitHub

https://github.com/hoviwang/kaiting
