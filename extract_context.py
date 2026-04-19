#!/usr/bin/env python3
"""
从 sessions_list 返回的 JSON 中提取"开庭"前的上下文。
用法: echo 'sessions_list 返回的完整 JSON' | python3 extract_context.py
"""
import json
import re
import sys

# 触发词（统一管理）
TRIGGER_PATTERN = re.compile(r"开庭|开一下庭|开庭审理|给我开", re.IGNORECASE)

# 负面情绪词
NEGATIVE_WORDS = [
    "不对", "不是", "错了", "敷衍", "没用", "不行",
    "垃圾", "烂", "有问题", "为什么", "怎么"
]


def extract_trigger_idx(messages):
    """找到触发词消息的索引"""
    for i in range(len(messages) - 1, -1, -1):
        content = messages[i].get("content", "")
        if isinstance(content, list):
            # content可能是 [{"type": "text", "text": "..."}] 格式
            content = " ".join(
                item.get("text", "") for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )
        if TRIGGER_PATTERN.search(str(content)):
            return i
    return -1


def extract_context(messages):
    """提取触发词前的上下文（保留原始时序）"""
    trigger_idx = extract_trigger_idx(messages)

    if trigger_idx <= 0:
        slice_start = max(0, len(messages) - 6)
        return messages[slice_start:]

    return messages[:trigger_idx]


def build_conversation_with_roles(before_msgs, max_len=800):
    """
    合并消息列表，标注role，保留原始时序。
    """
    lines = []
    truncated = False
    for m in before_msgs:
        role = m.get("role", "unknown")
        content = m.get("content", "")

        # 处理 content 为列表格式（如 [{"type":"text","text":"..."}]）
        if isinstance(content, list):
            content = " ".join(
                item.get("text", "") for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )
        content = str(content) if content else ""

        prefix = "🤖AI" if role == "assistant" else "👤用户"

        tag = ""
        if len(content) > max_len:
            content = content[:max_len] + "...[截断]"
            truncated = True

        lines.append(f"{prefix}: {content}")

    return "\n".join(lines), truncated


def infer_trigger_reason(trigger_msg, before_msgs):
    """推断触发原因"""
    content = trigger_msg.get("content", "") if trigger_msg else ""
    if isinstance(content, list):
        content = " ".join(
            item.get("text", "") for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    trigger_content = str(content)

    for neg in NEGATIVE_WORDS:
        if neg in trigger_content:
            return f"用户表达不满（关键词：{neg}）：{trigger_content[:100]}"

    敷衍_patterns = ["做不到", "无法", "不确定", "可能", "应该", "大概"]
    for m in before_msgs:
        if m.get("role") == "assistant":
            c = m.get("content", "")
            if isinstance(c, list):
                c = " ".join(item.get("text","") for item in c if isinstance(item, dict))
            c = str(c)
            for p in 敷衍_patterns:
                if p in c:
                    return f"AI回答含敷衍特征（检测到：{p}）：{c[:100]}"

    for m in reversed(before_msgs):
        if m.get("role") in ("user", "human"):
            c = m.get("content", "")
            if isinstance(c, list):
                c = " ".join(item.get("text","") for item in c if isinstance(item, dict))
            c = str(c)
            if len(c) > 10:
                return c[:150]

    return "用户主观不满，未明确原因"


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"JSON解析失败: {e}"}))
        sys.exit(1)

    # sessions_list 返回格式：{"sessions": [{"messages": [...]}, ...]}
    # 第一个 session 即当前 session
    sessions = data.get("sessions", [])
    if not sessions:
        print(json.dumps({"error": "sessions_list 返回为空，无法获取上下文"}))
        sys.exit(1)

    messages = sessions[0].get("messages", [])
    if not messages:
        print(json.dumps({"error": "当前 session 无消息历史"}))
        sys.exit(1)

    trigger_idx = extract_trigger_idx(messages)

    trigger_msg = None
    if trigger_idx >= 0:
        trigger_msg = messages[trigger_idx]

    before = extract_context(messages)

    ai_msgs = []
    user_msgs = []
    for m in before:
        role = m.get("role", "")
        content = m.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                item.get("text", "") for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )
        content = str(content)[:800]

        if role == "assistant":
            ai_msgs.append(content)
        elif role in ("user", "human"):
            user_msgs.append(content)

    conversation_with_roles, was_truncated = build_conversation_with_roles(before)

    result = {
        "trigger_reason": infer_trigger_reason(trigger_msg, before),
        "conversation_with_roles": conversation_with_roles,
        "ai_messages": ai_msgs,
        "user_messages": user_msgs,
        "before_count": len(before),
        "truncated": was_truncated
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
