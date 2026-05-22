pythonimport os
import requests
import json
import cloudscraper  # 專門用來繞過網站防爬驗證的套件

TG_BOT_TOKEN = "8694136579:AAFO2KKDbnE0_oQVt_Va5jOgPyXKXF4kHek"
TG_CHAT_ID = "-5259486832"

# 欲監控的地址清單 (鏈名稱小寫, 地址)
# 注意：免密鑰網頁端路徑的鏈名稱通常為小寫，例如：eth, bsc, tron, btc
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

def send_telegram_alert(message):
    """發送 Telegram 預警"""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print(f"【日誌輸出】:\n{message}")
        return
    url = f"https://telegram.org{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"發送通知失敗: {e}")

def check_address_without_key(chain, address):
    """免金鑰模擬瀏覽器查詢地址標記"""
    # 這是 OKLink 網頁前端真實呼叫的內部 API 網址
    url = f"https://oklink.com{chain}&address={address}"
    
    # 模擬一般 Chrome 瀏覽器的請求標頭 (Headers)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.oklink.com",
        "Referer": f"https://oklink.com{chain}/address/{address}"
    }

    try:
        # 使用 cloudscraper 代替普通的 requests 以繞過 Cloudflare 5秒盾
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"[{chain.upper()}] 請求失敗，狀態碼: {response.status_code} (可能觸發防爬)")
            return
            
        res_data = response.json()
        if res_data.get("code") != "0":
            print(f"[{chain.upper()}] 數據預載失敗: {res_data.get('msg')}")
            return

        data_list = res_data.get("data", [])
        if not data_list:
            print(f"[{chain.upper()}] 未找到該地址數據")
            return

        addr_info = data_list[0]
        
        # 提取網頁端標記與風險
        label = addr_info.get("label", "").strip()
        is_risk = addr_info.get("isRisk", False)

        if label:
            msg = f"⚠️ **【OKLink 免密鑰監控預警】**\n\n" \
                  f"🔗 **公鏈**: {chain.upper()}\n" \
                  f"🧱 **地址**: `{address}`\n" \
                  f"🏷️ **網頁標記**: *{label}*\n" \
                  f"🚨 **風險狀態**: {'危險' if is_risk else '普通標記'}"
            send_telegram_alert(msg)
        else:
            print(f"[{chain.upper()}] 地址 {address[:8]}... 暫無網頁標記。")

    except Exception as e:
        print(f"解析出錯 ({chain} - {address}): {e}")

if __name__ == "__main__":
    for chain, address in WATCH_LIST:
        check_address_without_key(chain, address)
