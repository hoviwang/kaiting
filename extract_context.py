#!/usr/bin/env python3
"""
从会话历史JSON中提取"开庭"前的上下文。
用法: echo '{"messages": [...]}' | python3 extract_context.py
"""
import json
import re
import sys

# 触发词（统一管理，三处同步）
TRIGGER_PATTERN = re.compile(r"开庭|开一下庭|开庭审理|给我开", re.IGNORECASE)

# 负面情绪词（用于推断触发原因）
NEGATIVE_WORDS = [
    "不对", "不是", "错了", "敷衍", "没用", "不行",
    "垃圾", "烂", "有问题", "为什么", "怎么", "不是"
]


def extract_trigger_idx(messages):
    """找到触发词消息的索引"""
    for i in range(len(messages) - 1, -1, -1):
        content = messages[i].get("content", "") or ""
        if TRIGGER_PATTERN.search(content):
            return i
    return -1


def extract_context(messages):
    """提取触发词前的上下文（保留原始时序）"""
    trigger_idx = extract_trigger_idx(messages)

    if trigger_idx <= 0:
        # 触发词在第一条或找不到，取最近6条
        slice_start = max(0, len(messages) - 6)
        return messages[slice_start:]

    # 取触发词前的所有消息（保留原始顺序）
    return messages[:trigger_idx]


def build_conversation_with_roles(before_msgs, max_len=800):
    """
    合并消息列表，标注role，保留原始时序。
    每条消息不超过max_len，过长截断并标记。
    """
    lines = []
    truncated = False
    for m in before_msgs:
        role = m.get("role", "unknown")
        content = m.get("content", "") or ""

        is_ai = role == "assistant"
        prefix = "🤖AI" if is_ai else "👤用户"

        tag = "truncated" if len(content) > max_len else None
        if tag:
            content = content[:max_len] + "...[截断]"
            truncated = True

        lines.append(f"{prefix}: {content}")

    return "\n".join(lines), truncated


def infer_trigger_reason(trigger_msg, before_msgs):
    """推断触发原因"""
    trigger_content = (trigger_msg.get("content", "") or "") if trigger_msg else ""

    # 检查触发消息本身是否包含负面词
    for neg in NEGATIVE_WORDS:
        if neg in trigger_content:
            return f"用户表达不满（关键词：{neg}）：{trigger_content[:100]}"

    # 检查历史消息中的AI回答是否有敷衍特征
   敷衍_patterns = ["做不到", "无法", "不确定", "可能", "应该", "大概"]
    for m in before_msgs:
        if m.get("role") == "assistant":
            content = m.get("content", "") or ""
            for p in 敷衍_patterns:
                if p in content:
                    return f"AI回答含敷衍特征（检测到：{p}）：{content[:100]}"

    # 找用户最后一条有意义的消息作为触发原因
    for m in reversed(before_msgs):
        if m.get("role") in ("user", "human"):
            content = m.get("content", "") or ""
            if len(content) > 10:
                return content[:150]

    return "用户主观不满，未明确原因"


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"JSON解析失败: {e}"}))
        sys.exit(1)

    messages = data.get("messages", [])
    trigger_idx = extract_trigger_idx(messages)

    # 触发词消息
    trigger_msg = None
    if trigger_idx >= 0:
        trigger_msg = messages[trigger_idx]

    # 提取上下文
    before = extract_context(messages)

    # 分类
    ai_msgs = []
    user_msgs = []
    for m in before:
        role = m.get("role", "")
        content = (m.get("content", "") or "")[:800]  # 保留800字符
        if role == "assistant":
            ai_msgs.append(content)
        elif role in ("user", "human"):
            user_msgs.append(content)

    # 合并时序输出（核心修复）
    conversation_with_roles, was_truncated = build_conversation_with_roles(before)

    result = {
        "trigger_reason": infer_trigger_reason(trigger_msg, before),
        "conversation_with_roles": conversation_with_roles,  # 保留时序 + role标注
        "ai_messages": ai_msgs,
        "user_messages": user_msgs,
        "before_count": len(before),
        "truncated": was_truncated
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
