import os
import json
import time
import random
import requests
from pathlib import Path

# =========================
# Telegram
# =========================

TG_BOT_TOKEN = "8694136579:AAFO2KKDbnE0_oQVt_Va5jOgPyXKXF4kHek"
TG_CHAT_ID = "-5259486832"

# =========================
# 地址列表
# =========================

TG_BOT_TOKEN = "8694136579:AAFO2KKDbnE0_oQVt_Va5jOgPyXKXF4kHek"

TG_CHAT_ID = "-5259486832"



# 欲監控的地址清單 (鏈名稱小寫, 地址)

WATCH_LIST = [

    ("tron", "TAkhPRkh49khbCRL89kDBixPo4qAwRgtLX"),

    ("tron", "TCRi4gorNNmD6gWmCrb9HzN9oYkJCeEn1Q"), 

    ("tron", "TNcZ2kS9553ereKLy5vNST5XDqakePhCAj"),

    ("tron", "TS7iwGakskLraZtc3iP45hXEpZGXykkLT6"), 

    ("tron", "TKmbY1FagdGw1oVk5fUS7AKN7aFnGG8q3H"),

    ("tron", "TYisoMcHMihcKmDqMTheBjgNoS7paTXKkg"), 

    ("tron", "TGNJ57Gd9zYuGuTLgeHQhyKRaXnDMJGmSS"),

    ("tron", "TEdqQfgR2W3pwmYPm4iUh2dPXBiJDPDceM"), 

    ("tron", "TU9yfMW7C9ybC87EgzjUj5T2f9desjZcm2"),

    ("tron", "TECk8FJFmRsHSiWGmGz99jShMuvB8TsRDR"), 

    ("tron", "TV2isXwYgr2jgtkRP4A8jtb7jw6UTkEhNQ"),

    ("tron", "TPR7b2B5SumonCzXrLN5B8FSUWw8u9BEgu"), 

    ("tron", "TEMXLzfuGEHiEPJimz1shtsR6tNUjyVtfQ"),

    ("tron", "TMfWQsjy9GNcaF4ViGLVB7NWKM6TUCXJ48"), 

    ("tron", "TAsbxyoopLYo4XAarpoDG7WuHucppvcMd7"),

]

# =========================
# 状态保存
# =========================

STATE_FILE = "state.json"

if Path(STATE_FILE).exists():
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        STATE = json.load(f)
else:
    STATE = {}

# =========================
# Telegram 推送
# =========================

def send_telegram(msg):

    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("未配置 Telegram")
        return

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TG_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }

    try:

        r = requests.post(
            url,
            json=payload,
            timeout=15
        )

        print("TG:", r.status_code)

    except Exception as e:
        print("TG失败:", e)

# =========================
# OKLink 网页接口
# =========================

def query_oklink(chain, address):

    url = f"https://www.oklink.com/{chain}/address/{address}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:

        r = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        print(
            f"{address[:8]} HTTP:",
            r.status_code
        )

        if r.status_code != 200:
            return None

        return r.text.lower()

    except Exception as e:

        print("请求失败:", e)

        return None

# =========================
# 检查标签
# =========================

def check_address(chain, address):

    data = query_oklink(chain, address)

    if not data:
        return

    text = data

    keywords = [
        "scam",
        "fraud",
        "gambling",
        "博彩",
        "赌博",
        "mixer",
        "黑钱",
        "洗钱",
        "high risk",
        "sanction",
        "phishing",
        "诈骗",
        "黑名单"
    ]

    matched = []

    lower_text = text.lower()

    for k in keywords:

        if k.lower() in lower_text:
            matched.append(k)

    current = ",".join(sorted(set(matched)))

    old = STATE.get(address)

    print(
        f"{address[:8]} 当前标签:",
        current if current else "无"
    )

    # 初始化
    if old is None:
        STATE[address] = current
        return

    # 标签变化
    if old != current:

        msg = (
            f"⚠️ 地址风险标签变化\n\n"
            f"链: {chain.upper()}\n"
            f"地址:\n`{address}`\n\n"
            f"旧标签:\n{old or '无'}\n\n"
            f"新标签:\n{current or '无'}"
        )

        send_telegram(msg)

        STATE[address] = current
# =========================
# 主程序
# =========================

if __name__ == "__main__":

    for chain, address in WATCH_LIST:

        check_address(chain, address)

        # 随机延迟
        time.sleep(random.randint(3, 8))

    with open(STATE_FILE, "w", encoding="utf-8") as f:

        json.dump(
            STATE,
            f,
            ensure_ascii=False,
            indent=2
        )
