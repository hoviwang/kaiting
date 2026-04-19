---
name: 开庭
description: 杠精评审技能。当用户说「开庭」（含变体），主会话提取上下文后触发sub-agent，以杠精人格审查AI刚才的回答，揪出偷懒/敷衍/单渠道等问题，逼AI多渠道查证、检讨、并给出更多解决方案。
version: 2.1.0
author: hoviwang
tags: [productivity, debugging, self-improvement]
trigger: 开庭|开一下庭|开庭审理|给我开
---

# ai-critic — 杠精评审 v2.1

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
主agent 启动 sub-agent（杠精人格 + 工具集）
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

调用 `sessions_list`，传入当前 session 的 key，获取消息历史：

```
sessions_list，sessionKey=<当前sessionKey>，limit=10，messageLimit=20
```

结果 JSON 传给 extract_context.py。

### 步骤2：提取上下文

```bash
python3 ~/.openclaw/skills/开庭.skill/extract_context.py << 'EOF'
<sessions_list 返回的完整 JSON>
EOF
```

脚本输出：
- `trigger_reason`：触发原因
- `conversation_with_roles`：保留时序的对话（含role标注）
- `ai_messages`：AI 刚才的回答
- `user_messages`：用户之前的消息
- `before_count`：上下文消息条数

### 步骤3：检查提取结果

如果脚本返回 `{"error": "..."}`：
→ 直接向用户展示错误，并用**人工方式**继续开庭流程：
  - 让用户描述「刚才AI哪个回答有问题」
  - 人工启动 sub-agent 挑刺

### 步骤4：启动 sub-agent

使用 `sessions_spawn`，传递上下文，配置工具集：

```
web_search, minimax__web_search, memory_search, sessions_history
```

sub-agent 必须完成三部分：**挑刺 → 追问 → 示范**

### 步骤5：展示结果，**询问用户确认**

展示 sub-agent 输出，**必须询问用户确认**：

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

### 步骤6：等用户确认后执行

| 用户选择 | 主agent动作 |
|---------|-------------|
| 继续深挖 | 按追问方向实际查证，查完再展示，再问确认 |
| 够了，进检讨 | 输出强制检讨格式 |
| 方向偏了 | 重新调用 sub-agent |
| 不够狠 | 重新调用 sub-agent，语气升级 |

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
├── README.md             # 完整使用说明（中英双语）
├── extract_context.py    # 上下文提取脚本
└── references/
    └── subagent-prompt.md # sub-agent 完整指令
```

## GitHub

https://github.com/hoviwang/kaiting
