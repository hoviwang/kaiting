---
name: 开庭
description: 杠精评审技能。当用户说「开庭」（含变体），主会话提取上下文后触发sub-agent，以杠精人格审查AI刚才的回答，揪出偷懒/敷衍/单渠道等问题，逼AI多渠道查证、检讨、并给出更多解决方案。
version: 2.2.0
author: hoviwang
tags: [productivity, debugging, self-improvement]
trigger: 开庭|开一下庭|开庭审理|给我开
---

# ai-critic — 杠精评审 v2.2

## 😤 受够了 AI 的敷衍？

回答一半、偷懒跳步、单渠道给答案、说完"做不到"就没下文——

说「**开庭**」，摇一个杠精评审来治它。

---

## 安装说明（AI 自动执行）

当用户说「阅读本文件并安装」，AI 必须执行以下命令：

```bash
mkdir -p ~/.openclaw/skills/开庭.skill
git clone https://github.com/hoviwang/kaiting.git /tmp/kaiting-repo
cp -r /tmp/kaiting-repo/. ~/.openclaw/skills/开庭.skill/
chmod +x ~/.openclaw/skills/开庭.skill/extract_context.py
rm -rf /tmp/kaiting-repo
ls ~/.openclaw/skills/开庭.skill/
```

安装完成后报告：
```
✅ 「开庭」技能安装完成！
重启 OpenClaw 后直接说「开庭」即可使用。
```

---

## 工作流程

```
用户说"开庭"
  ↓
主agent 调用 sessions_list 获取当前会话消息
  ↓
主agent 运行 extract_context.py 提取上下文
  ↓
  ├── 能拿到 → 正常流程：启动 sub-agent 挑刺
  └── 拿不到 → 询问用户「刚才发生了什么？」
      → 用户口述问题
      → 直接启动 sub-agent 挑刺用户描述的场景
  ↓
sub-agent 三步输出：【挑刺】→【追问】→【示范】
  ↓
主agent 展示结果，询问用户确认
  ↓
用户：「继续深挖」/ 「够了，进检讨」/ 「方向偏了」
  ↓
按用户选择执行
```

---

## 主agent执行步骤

### 步骤1：获取会话消息

调用 `sessions_list`，获取当前 session 的消息历史：

```
sessions_list，limit=5，messageLimit=30
```

### 步骤2：提取上下文

```bash
python3 ~/.openclaw/skills/开庭.skill/extract_context.py << 'EOF'
<sessions_list 返回的完整 JSON>
EOF
```

### 步骤3：判断结果

**如果 `fallback: false`**（正常拿到上下文）：
→ 继续步骤4

**如果 `fallback: true`**（拿不到上下文）：
→ 直接问用户：「刚才发生了什么？AI哪个回答有问题？」
→ 拿到用户回复后，跳到步骤5，直接用用户描述的场景启动 sub-agent

### 步骤4：启动 sub-agent（有上下文时）

使用 `sessions_spawn`，传递 extract_context.py 的输出结果。

### 步骤5：启动 sub-agent（无上下文 / 用户口述时）

用户描述「刚才AI哪里有问题」之后，直接用那段描述作为上下文，启动 sub-agent：

prompt 示例：
```
用户反映：「（用户口述的问题描述）」

请作为杠精评审，对AI的回答进行挑刺。
输出【挑刺】【追问】【示范】三部分。
```

### 步骤6：展示结果，询问用户确认

```
【开庭结果】

【挑刺】
（sub-agent 输出）

【追问】
（sub-agent 输出）

【示范】
（sub-agent 输出）

---
以上是评审结果。
要继续吗？
  → 继续深挖：针对【追问】方向继续查证
  → 够了，进检讨：进入检讨环节
  → 方向偏了：换一个角度重新挑刺
  → 不够狠：重新挑刺，语气更冲
```

### 步骤7：强制检讨格式

```
【检讨】
1. 我刚才哪里偷懒/敷衍了：（具体说，有原文引用）
2. 我应该多查/多想这些渠道：① ② ③
3. 接下来我打算试这三步：
   ① ...
   ② ...
   ③ ...
```

### 步骤8：按检讨执行

说完检讨要**真的动手**，不能完就结束。

---

## 杠精评判标准

| 场景 | 判定标准 |
|------|---------|
| 单渠道 | 只用一种信息源就给结论 |
| 敷衍 | 说"做不到"但没给替代方案 |
| 话术 | 用套话绕开问题核心 |
| 犟嘴 | 被问后找借口不认错 |
| 跳过验证 | 没确认就给结论 |
| 不够深 | 浅尝辄止，没追问根源 |
| 主观触发 | 用户觉得不满意（无需明确理由） |

---

## 用户反馈处理

| 用户回复 | 主agent动作 |
|---------|-------------|
| 继续 / 继续挖 | 按追问方向实际执行 web_search 等工具 |
| 够了 / 进检讨 | 输出检讨格式 |
| 方向偏了 | 重新调用 sub-agent |
| 不够狠 | 重新调用 sub-agent，语气更冲 |

---

## 文件结构

```
~/.openclaw/skills/开庭.skill/
├── SKILL.md              # 本文件
├── README.md             # 完整使用说明
├── extract_context.py    # 上下文提取脚本
└── references/
    └── subagent-prompt.md # sub-agent 完整指令
```

## GitHub

https://github.com/hoviwang/kaiting
