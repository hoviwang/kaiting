# ai-critic 杠精评审

(enGLISH version at bottom)

---

## 😤 受够了 AI 的敷衍？

回答一半、偷懒跳步、单渠道给答案、说完"做不到"就没下文——

说「**开庭**」，摇一个杠精评审来治它。

---

## 这是什么

当你说「开庭」，AI 会：
1. 提取刚才的对话上下文
2. 派出一个杠精 sub-agent 逐条挑刺
3. 逼出你没想过的追问方向 + 正确做法的示范
4. 然后 AI 必须认真检讨，给出可执行的改进行动

不是骂完就完，是骂完**必须改**。

---

## 触发词

| 中文 | English |
|------|---------|
| 开庭 | Open court |
| 开一下庭 | |
| 开庭审理 | |
| 给我开 | |

---

## 工作流程

```
用户说"开庭"
  ↓
主 agent 提取上下文（会话历史）
  ↓
启动 sub-agent（杠精人格 + 工具集）
  ↓
sub-agent 三步输出：
  【挑刺】→【追问】→【示范】
  ↓
主 agent 展示结果，询问用户确认
  ↓
用户：「继续深挖」/ 「够了，进检讨」/ 「方向偏了，换角度」
  ↓
按用户选择执行
```

---

## 文件结构

```
ai-critic/
├── SKILL.md                        # 主技能说明
├── README.md                       # 本文件
├── extract_context.py              # 上下文提取脚本
└── references/
    └── subagent-prompt.md          # sub-agent 完整指令
```

---

## 主 agent 执行步骤

### 步骤1：提取上下文

1. 用 `sessions_history` 获取当前会话最近 30 条消息
2. 将 JSON 传给提取脚本：

```bash
python3 ~/.openclaw/skills/ai-critic/extract_context.py << 'EOF'
<paste JSON>
EOF
```

脚本输出：
- `trigger_reason`：触发原因
- `conversation_with_roles`：保留时序的对话（含role标注）
- `ai_messages`：AI 刚才的回答
- `user_messages`：用户之前的消息

### 步骤2：启动 sub-agent

使用 `sessions_spawn`，传递上下文，配置工具集：

```
web_search, minimax__web_search, memory_search, sessions_history
```

sub-agent 必须完成三部分：**挑刺 → 追问 → 示范**

### 步骤3：展示结果，询问用户确认

展示 sub-agent 的【挑刺】【追问】【示范】后，**必须询问用户确认**：

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
```

### 步骤4：执行用户选择

| 用户选择 | 主 agent 动作 |
|---------|--------------|
| 继续深挖 | 按追问方向实际执行 web_search 等工具查证，再展示结果，再问确认 |
| 够了，进检讨 | 输出强制检讨格式（见下方） |
| 方向偏了 | 重新调用 sub-agent，换角度再挑 |

### 步骤5：强制检讨格式

```
【检讨】
1. 我刚才哪里偷懒/敷衍了：（具体说，有原文引用）
2. 我应该多查/多想这些渠道：① ② ③
3. 接下来我打算试这三步：
   ① ...
   ② ...
   ③ ...
```

### 步骤6：按检讨执行

说完检讨要**真的动手**，不能完就结束。

---

## 杠精评判标准

| 场景 | 判定 |
|------|------|
| 单渠道 | 只用一种信息源就给结论 |
| 敷衍 | 说做不到但没给替代方案 |
| 话术 | 用套话绕开核心问题 |
| 犟嘴 | 被问后找借口不认错 |
| 跳过验证 | 没确认就给结论 |
| 不够深 | 浅尝辄止，没追问根源 |
| 主观触发 | 用户觉得不满意（无需明确理由）|

---

## 用户反馈处理

| 用户回复 | 主 agent 动作 |
|---------|--------------|
| 继续 / 继续挖 | 按追问方向实际执行 web_search |
| 够了 / 进检讨 | 输出检讨格式 |
| 方向偏了 | 重新调用 sub-agent |
| 不够狠 | 重新调用 sub-agent，加强语气 |

---

<br>

---

# ai-critic — AI Critic Skill (English)

## 😤 Tired of AI Slacking Off?

Half-baked answers, skipping steps, single-source responses, saying "can't do" with no alternatives —

Say **"开庭" (Open court)** to summon a nitpicker critic.

---

## What It Does

When you say "开庭", the AI will:
1. Extract the recent conversation context
2. Deploy a sub-agent with a nitpicker personality to dissect every flaw
3. Force out question directions you haven't considered + a correct approach demo
4. Then the AI must seriously reflect and produce actionable improvements

Not just venting — **必须有实际改变**。

## Trigger Words

| English | Chinese |
|--------|---------|
| Open court | 开庭 |
| 开一下庭 | |
| 开庭审理 | |
| 给我开 | |

## Workflow

```
User says "开庭"
  ↓
Main agent extracts context (conversation history)
  ↓
Launch sub-agent (nitpicker + toolset)
  ↓
sub-agent three-part output:
  【挑刺】Criticize → 【追问】Probe → 【示范】Demonstrate
  ↓
Main agent shows results, asks user to confirm
  ↓
User: "Continue digging" / "Enough, start reflection" / "Off-topic, switch angle"
  ↓
Execute user's choice
```

## Files

```
ai-critic/
├── SKILL.md                        # Main skill description
├── README.md                       # This file
├── extract_context.py              # Context extraction script
└── references/
    └── subagent-prompt.md          # sub-agent full instructions
```

## Main Agent Steps

### Step 1: Extract context

Use `sessions_history` tool to get the last 30 messages, pipe to extract script.

### Step 2: Spawn sub-agent

Use `sessions_spawn` with tools: `web_search, minimax__web_search, memory_search, sessions_history`

### Step 3: Show results, ask user to confirm

Present the three sections, then **ask for user confirmation**:

```
【开庭结果】
【挑刺】(sub-agent output)
【追问】(sub-agent output)
【示范】(sub-agent output)

Continue?
  → Continue digging: investigate the 【追问】 directions
  → Enough, start reflection: enter reflection section
  → Off-topic: switch angle and retry
```

### Step 4: Execute user's choice

### Step 5: Mandatory reflection format

```
【检讨 / Reflection】
1. Where was I lazy/perfunctory: (specific, with quotes)
2. I should have checked these channels: ① ② ③
3. My next three steps:
   ① ...
   ② ...
   ③ ...
```

### Step 6: Execute the reflection

Must **actually try** the steps, not just stop after writing them.

## Judging Criteria

| Scenario |判定 |
|----------|------|
| Single source | Only used one info source |
| Perfunctory | Said "can't do" without alternatives |
| Fluff/Talking points | Used filler phrases to dodge core |
| Stubborn | Made excuses instead of admitting fault |
| Skipped verification | Gave conclusions without confirming |
| Shallow | Stopped at surface level |
| Subjective trigger | User dissatisfied (no reason needed) |

## User Feedback

| User says | Main agent does |
|-----------|----------------|
| Continue / 继续挖 | Investigate 【追问】 directions with web_search |
| Enough / 够了 | Output reflection format |
| Off-topic / 方向偏了 | Respawn sub-agent with different angle |
| Not harsh enough / 不够狠 | Respawn sub-agent, stronger tone |
