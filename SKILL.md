---
name: 开庭
description: 杠精评审技能。当用户说「开庭」（含变体），主会话提取上下文后触发sub-agent，以杠精人格审查AI刚才的回答，揪出偷懒/敷衍/单渠道等问题，逼AI多渠道查证、检讨、并给出更多解决方案。
version: 2.4.0
author: hoviwang
tags: [productivity, debugging, self-improvement]
trigger: 开庭|开一下庭|开庭审理|给我开
---

# ai-critic — 杠精评审 v2.4

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
  ├── 能拿到 → 正常流程
  └── 拿不到 → 询问用户「刚才发生了什么？」
      → 用户口述问题
      → 直接用用户描述的场景启动 sub-agent
  ↓
sub-agent 三步输出：【挑刺】→【追问】→【示范】
  ↓
主agent 展示结果，询问用户确认
  ↓
用户选择：
  → 继续深挖：针对【追问】方向查证，查完再问确认
  → 够了，进检讨：进入【检讨】环节
  → 方向偏了：重新调用 sub-agent 挑刺
  → 不够狠：重新调用 sub-agent，气势更冲
  ↓
【检讨】输出后，用户确认 → 主agent执行检讨中列出的行动
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

**如果 `fallback: false`** → 继续步骤4
**如果 `fallback: true`** → 直接问用户：「刚才发生了什么？AI哪个回答有问题？」→ 拿到回复后跳到步骤5

### 步骤4 & 5：启动 sub-agent

使用 `sessions_spawn`，传递 extract_context.py 的输出（触发原因、对话时序、AI消息、用户消息）。

sub-agent 必须完成三部分：**挑刺 → 追问 → 示范**

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

### 步骤7：执行用户选择

| 用户回复 | 主agent动作 |
|---------|-------------|
| 继续深挖 | 按追问方向实际执行 web_search 等工具，查完再展示，再问确认 |
| 够了 / 进检讨 | 进入【检讨】环节 |
| 方向偏了 | 重新调用 sub-agent |
| 不够狠 | 重新调用 sub-agent，语气更冲 |

---

## 【检讨】环节

用户选择「够了，进检讨」后，主agent 输出检讨内容，**等用户确认后再执行**。

### 步骤A：输出检讨

```
【检讨】

1. 我刚才哪里偷懒/敷衍了：
   （具体说，有原文引用，指出AI哪句话、哪个行为是偷懒/敷衍/犟嘴）

2. 我应该多查/多想这些渠道：
   ① （第一个应该查但没查的渠道/角度）
   ② （第二个）
   ③ （第三个）

3. 接下来我打算试这三步：
   ① ...（具体行动，不是说说而已）
   ② ...
   ③ ...
```

### 步骤B：等用户确认

```
---
检讨输出完毕。
确认执行吗？
  → 可以，执行吧：按检讨里的三步真的动手
  → 哪里不对：指出问题，我重新检讨
  → 还不够：补充更多要查的渠道/行动
```

### 步骤C：用户确认后执行

用户说「可以，执行吧」后，主agent **按检讨里列出的行动逐一执行**：
- 说要「查某个信息源」→ 立即调用 web_search / minimax__web_search 实际去查
- 说要「修正某个错误」→ 立即执行修正
- 说要「重试某个操作」→ 立即重试

执行完后报告结果，再问用户：「执行完毕，要继续深挖吗？」

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

## 文件结构

```
~/.openclaw/skills/开庭.skill/
├── SKILL.md              # 本文件
├── README.md             # 完整使用说明
├── extract_context.py     # 上下文提取脚本
└── references/
    └── subagent-prompt.md # sub-agent 完整指令
```

## GitHub

https://github.com/hoviwang/kaiting
