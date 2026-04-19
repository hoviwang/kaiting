#!/usr/bin/env python3
"""
开庭上下文提取脚本 v3

fallback 策略：
1. 优先用 sessions_list 返回的 messages（有上下文）
2. 拿不到 → 返回 fallback 标志，主 agent 改为询问用户"刚才发生了什么"
"""
import json
import re
import sys

TRIGGER_PATTERN = re.compile(r"开庭|开一下庭|开庭审理|给我开", re.IGNORECASE)

NEGATIVE_WORDS = [
    "不对", "不是", "错了", "敷衍", "没用", "不行",
    "垃圾", "烂", "有问题", "为什么", "怎么"
]


def extract_trigger_idx(messages):
    for i in range(len(messages) - 1, -1, -1):
        content = messages[i].get("content", "")
        if isinstance(content, list):
            content = " ".join(
                item.get("text", "") for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )
        if TRIGGER_PATTERN.search(str(content)):
            return i
    return -1


def extract_context(messages):
    trigger_idx = extract_trigger_idx(messages)
    if trigger_idx <= 0:
        slice_start = max(0, len(messages) - 6)
        return messages[slice_start:]
    return messages[:trigger_idx]


def build_conversation_with_roles(before_msgs, max_len=800):
    lines = []
    truncated = False
    for m in before_msgs:
        role = m.get("role", "unknown")
        content = m.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                item.get("text", "") for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )
        content = str(content) if content else ""

        prefix = "🤖AI" if role == "assistant" else "👤用户"
        if len(content) > max_len:
            content = content[:max_len] + "...[截断]"
            truncated = True
        lines.append(f"{prefix}: {content}")

    return "\n".join(lines), truncated


def infer_trigger_reason(trigger_msg, before_msgs):
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
                c = " ".join(item.get("text", "") for item in c if isinstance(item, dict))
            c = str(c)
            for p in 敷衍_patterns:
                if p in c:
                    return f"AI回答含敷衍特征（检测到：{p}）：{c[:100]}"

    for m in reversed(before_msgs):
        if m.get("role") in ("user", "human"):
            c = m.get("content", "")
            if isinstance(c, list):
                c = " ".join(item.get("text", "") for item in c if isinstance(item, dict))
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

    # sessions_list 格式：{"sessions": [{"messages": [...]}, ...]}
    sessions = data.get("sessions", [])
    if not sessions:
        # Fallback: 告诉主agent改为询问用户"刚才发生了什么"
        print(json.dumps({
            "fallback": True,
            "fallback_prompt": "无法从会话历史获取上下文。请询问用户：「刚才发生了什么？AI哪个回答有问题？」拿到回答后，直接启动 sub-agent 进行挑刺。"
        }))
        sys.exit(0)

    messages = sessions[0].get("messages", [])
    if not messages:
        print(json.dumps({
            "fallback": True,
            "fallback_prompt": "当前会话无消息历史。请询问用户：「刚才发生了什么？AI哪个回答有问题？」拿到回答后，直接启动 sub-agent 进行挑刺。"
        }))
        sys.exit(0)

    trigger_idx = extract_trigger_idx(messages)
    trigger_msg = messages[trigger_idx] if trigger_idx >= 0 else None
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
        "fallback": False,
        "trigger_reason": infer_trigger_reason(trigger_msg, before),
        "conversation_with_roles": conversation_with_roles,
        "ai_messages": ai_msgs,
        "user_messages": user_msgs,
        "before_count": len(before),
        "truncated": was_truncated
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
