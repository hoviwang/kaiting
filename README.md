# ai-critic — 杠精评审

[English](#english) | [中文](#中文)

---

## 中文

### 😤 受够了 AI 的敷衍？

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

## 安装

### 前置要求

- Python 3.8+
- `sessions_history` 工具（用于获取对话历史）
- `sessions_spawn` 工具（用于启动 sub-agent）
- `web_search` / `minimax__web_search` 工具（用于多渠道查证）
- `memory_search` 工具（可选，用于查长期记忆）

### OpenClaw 部署步骤

**步骤 1：复制到 skills 目录**

```bash
# 在 OpenClaw 运行环境中
cp -r /path/to/kaiting ~/.openclaw/skills/kaiting.skill
```

**步骤 2：确认文件结构**

```
~/.openclaw/skills/kaiting.skill/
├── SKILL.md              # OpenClaw 专用（会自动触发）
├── README.md             # 本文件
├── extract_context.py     # 上下文提取脚本
└── references/
    └── subagent-prompt.md  # sub-agent 完整指令
```

**步骤 3：设置触发词**

在 OpenClaw 中说一次「开庭」，系统会自动识别触发。

---

## 使用方法

### 快速开始

在支持 OpenClaw 的对话中，直接说：

```
开庭
```

AI 会自动进入杠精评审流程。

### 完整流程（开发者参考）

#### Step 1：提取上下文

用 `sessions_history` 获取最近 30 条消息，将 JSON 传给提取脚本：

```bash
python3 ~/.openclaw/skills/kaiting.skill/extract_context.py << 'EOF'
<paste sessions_history 返回的 JSON>
EOF
```

脚本输出：

```json
{
  "trigger_reason": "用户表达不满（关键词：敷衍）",
  "conversation_with_roles": "👤用户: ...\n🤖AI: ...\n👤用户: ...",  // 保留时序
  "ai_messages": ["AI回答1", "AI回答2"],
  "user_messages": ["用户消息1", "用户消息2"],
  "before_count": 6,
  "truncated": false
}
```

#### Step 2：启动 sub-agent

使用 `sessions_spawn`，传递上下文，配置工具集：

```
tools: web_search, minimax__web_search, memory_search, sessions_history
```

sub-agent 必须完成三部分：**挑刺 → 追问 → 示范**

#### Step 3：展示结果，询问用户确认

```
【开庭结果】

【挑刺】
（sub-agent 逐条列出问题）

【追问】
（2-3个主AI完全没有想过的问题方向）

【示范】
（step by step 正确做法演示）

---
以上是评审结果。要继续吗？
  → 继续深挖：针对【追问】方向继续查证
  → 够了，进检讨：进入检讨环节
  → 方向偏了：换一个角度重新挑刺
  → 不够狠：重新挑刺，语气更冲
```

#### Step 4：执行用户选择

| 用户选择 | 主 agent 动作 |
|---------|--------------|
| 继续深挖 | 按追问方向实际执行 web_search 等工具查证，查完再展示，再问确认 |
| 够了，进检讨 | 输出强制检讨格式（见下方） |
| 方向偏了 | 重新调用 sub-agent，换角度 |
| 不够狠 | 重新调用 sub-agent，语气升级 |

#### Step 5：强制检讨格式

```
【检讨】
1. 我刚才哪里偷懒/敷衍了：（具体说，有原文引用）
2. 我应该多查/多想这些渠道：① ② ③
3. 接下来我打算试这三步：
   ① ...
   ② ...
   ③ ...
```

#### Step 6：按检讨执行

说完检讨要**真的动手**，不能完就结束。

---

## 排障清单

### Q：说"开庭"没有反应？

**可能原因**：
- OpenClaw 未加载该 skill → 检查 `~/.openclaw/skills/` 下是否有 `aiting.skill` 目录
- 触发词格式不对 → 确认说「开庭」（不是"开庭审理"之类变体第一次触发时系统自动识别）

### Q：extract_context.py 报错 "JSON 解析失败"？

**原因**：sessions_history 返回的不是合法 JSON

**解决**：确认 sessions_history 工具返回格式，extract_context.py 期望 `{ "messages": [...] }` 结构

### Q：sub-agent 输出乱码或空？

**原因**：`conversation_with_roles` 为空 → 没有找到触发词或消息列表为空

**解决**：检查 sessions_history 消息数量是否 ≥ 2

### Q：trigger_reason 推断不准确？

**当前逻辑**：
1. 触发词消息是否含负面词（不对/敷衍/烂/垃圾...）
2. 历史中 AI 回复是否含敷衍特征（做不到/不确定/大概...）
3. 用户最后一条有意义的消息

如需更精确，可在 `extract_context.py` 的 `NEGATIVE_WORDS` 和 `敷衍_patterns` 列表中增减关键词。

### Q：web_search 等工具报权限错误？

**原因**：sub-agent 工具集中某些工具未启用

**解决**：确认部署环境支持以下工具：
- `web_search`（Tavily）
- `minimax__web_search`（MiniMax）
- `sessions_history`
- `memory_search`

### Q：评审结果"方向偏了"？

**说明**：sub-agent 的 goal prompt 中已经注入了触发原因和对话上下文，方向偏说明上下文传递有问题，或 sub-agent 理解有误

**解决**：
1. 检查 extract_context.py 输出是否正确
2. 在 sub-agent goal 中补充更具体的"禁止方向"

---

## 触发词（含变体）

| 中文 | English |
|------|---------|
| 开庭 | Open court |
| 开一下庭 | |
| 开庭审理 | |
| 给我开 | |

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
| 主观触发 | 用户觉得不满意（无需明确理由） |

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | OpenClaw 专用（自动触发，不兼容其他平台） |
| `README.md` | 本文件 |
| `extract_context.py` | 上下文提取脚本（通用 Python，可独立使用） |
| `references/subagent-prompt.md` | sub-agent 完整指令（通用） |

---

<br>

---

## English

### 😤 Tired of AI Slacking Off?

Half-baked answers, skipping steps, single-source responses, saying "can't do" with no alternatives —

Say **"开庭" (Open court)** to summon a nitpicker critic.

---

## What It Is

When you say "开庭", the AI will:

1. Extract the recent conversation context
2. Deploy a sub-agent with a nitpicker personality to dissect every flaw
3. Force out question directions you haven't considered + a correct approach demo
4. Then the AI must seriously reflect and produce actionable improvements

Not just venting — **必须有实际改变**.

---

## Installation

### Prerequisites

- Python 3.8+
- `sessions_history` tool (to fetch conversation history)
- `sessions_spawn` tool (to launch sub-agent)
- `web_search` / `minimax__web_search` tool (for multi-channel verification)
- `memory_search` tool (optional)

### OpenClaw Deployment

**Step 1: Copy to skills directory**

```bash
cp -r /path/to/kaiting ~/.openclaw/skills/kaiting.skill
```

**Step 2: Verify file structure**

```
~/.openclaw/skills/kaiting.skill/
├── SKILL.md                  # OpenClaw-specific (auto-triggered)
├── README.md                 # This file
├── extract_context.py        # Context extraction script
└── references/
    └── subagent-prompt.md   # Sub-agent full instructions
```

**Step 3: Trigger**

Just say "开庭" once in a supported OpenClaw conversation. The system will auto-recognize the trigger.

---

## How to Use

### Quick Start

In an OpenClaw-supported conversation, simply say:

```
开庭
```

The AI will automatically enter the critic review flow.

### Full Flow (Developer Reference)

#### Step 1: Extract context

Use `sessions_history` to get the last 30 messages, pipe JSON to the extract script:

```bash
python3 ~/.openclaw/skills/kaiting.skill/extract_context.py << 'EOF'
<paste sessions_history JSON>
EOF
```

Output:

```json
{
  "trigger_reason": "User expressed dissatisfaction (keyword:敷衍)",
  "conversation_with_roles": "👤User: ...\n🤖AI: ...\n👤User: ...",  // Time-order preserved
  "ai_messages": ["AI answer 1", "AI answer 2"],
  "user_messages": ["User message 1", "User message 2"],
  "before_count": 6,
  "truncated": false
}
```

#### Step 2: Spawn sub-agent

Use `sessions_spawn` with tools:

```
tools: web_search, minimax__web_search, memory_search, sessions_history
```

Sub-agent must complete three parts: **Criticize → Probe → Demonstrate**

#### Step 3: Show results, ask user to confirm

```
【开庭结果 / Court Result】

【挑刺 / Criticize】
(sub-agent output)

【追问 / Probe】
(2-3 question directions the AI never considered)

【示范 / Demonstrate】
(step by step correct approach)

---
以上是评审结果。要继续吗？

Continue?
  → Continue digging: investigate the 【追问】 directions
  → Enough, enter reflection: go to reflection section
  → Off-topic: switch angle and retry
  → Not harsh enough: retry with stronger tone
```

#### Step 4: Execute user's choice

| Choice | Main agent action |
|--------|------------------|
| Continue digging | Actually run web_search etc. on 【追问】 directions, show results, ask again |
| Enough, enter reflection | Output mandatory reflection format |
| Off-topic | Respawn sub-agent with different angle |
| Not harsh enough | Respawn sub-agent with stronger tone |

#### Step 5: Mandatory reflection format

```
【检讨 / Reflection】
1. Where was I lazy/perfunctory: (specific, with quotes)
2. I should have checked these channels: ① ② ③
3. My next three steps:
   ① ...
   ② ...
   ③ ...
```

#### Step 6: Execute the reflection

Must **actually try** the steps, not just stop after writing them.

---

## Troubleshooting

### Q: "开庭" doesn't trigger anything?

**Possible cause**: Skill not loaded → check `~/.openclaw/skills/` for `aiting.skill` directory

**Fix**: Ensure the skill folder is correctly placed

### Q: extract_context.py throws "JSON parse error"?

**Cause**: sessions_history didn't return valid JSON

**Fix**: Verify sessions_history tool returns `{ "messages": [...] }` structure

### Q: sub-agent output is garbled or empty?

**Cause**: `conversation_with_roles` is empty → trigger not found or empty message list

**Fix**: Check that sessions_history returned ≥ 2 messages

### Q: trigger_reason inference is inaccurate?

**Current logic**:
1. Does trigger message contain negative words (不对/敷衍/烂/垃圾...)?
2. Do AI responses in history contain slack indicators (做不到/不确定/大概...)?
3. User's last meaningful message

Adjust `NEGATIVE_WORDS` and `敷衍_patterns` in `extract_context.py` for more precision.

### Q: web_search tools report permission errors?

**Cause**: Some tools in sub-agent toolset not enabled in deployment environment

**Fix**: Confirm deployment environment supports:
- `web_search` (Tavily)
- `minimax__web_search` (MiniMax)
- `sessions_history`
- `memory_search`

### Q: Results are "off-topic"?

**Note**: Sub-agent's goal prompt already injects trigger reason and conversation context. Off-topic means either context delivery failed or sub-agent misunderstood.

**Fix**:
1. Verify extract_context.py output is correct
2. Inject more specific "prohibited directions" in sub-agent goal

---

## Trigger Words

| English | Chinese |
|---------|---------|
| Open court | 开庭 |
| 开一下庭 | |
| 开庭审理 | |
| 给我开 | |

---

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

---

## File Reference

| File | Description |
|------|-------------|
| `SKILL.md` | OpenClaw-specific (auto-trigger, not compatible with other platforms) |
| `README.md` | This file |
| `extract_context.py` | Context extraction script (generic Python, standalone) |
| `references/subagent-prompt.md` | Sub-agent full instructions (generic) |
