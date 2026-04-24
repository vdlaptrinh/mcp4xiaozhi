from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import sys
import logging
import re
import random

logger = logging.getLogger("MCP-History")
logging.basicConfig(level=logging.INFO)

LICHNGAY_URL = "https://lichngaytot.com/ngay-nay-nam-xua.html"
NEWS_URL = "https://vnexpress.net/rss/tin-moi-nhat.rss"
STORIES_URL = "https://dailuu.wordpress.com/2024/12/28/23-mau-chuyen-ngan-va-nhung-bai-hoc-cuoc-doi-rut-ra-tu-do/"
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}

mcp = FastMCP("MCP-History")

_stories_cache = None

def get_date(opt="TODAY"):
    today = datetime.now()
    if opt == "YESTERDAY":
        return today - timedelta(days=1)
    elif opt == "TOMORROW":
        return today + timedelta(days=1)
    return today

def clean_content(content):
    if not content:
        return "Không tìm thấy nội dung lịch sử hôm nay."
    combined_text = " ".join(" ".join(el.get_text().strip().split()) for el in content)
    date_pattern = r"\b(\d{1,2}-\d{1,2}-\d{4})\b"
    seen_dates = set()
    def remove_duplicates(match):
        date = match.group(1)
        if date in seen_dates:
            return ""
        seen_dates.add(date)
        return date
    cleaned_text = re.sub(date_pattern, remove_duplicates, combined_text)
    return ' '.join(cleaned_text.split())

def fetch_history(opt="TODAY"):
    try:
        selected_date = get_date(opt)
        payload = {'ngayxem': f"{selected_date.day:02d}-{selected_date.month:02d}-{selected_date.year}"}
        response = requests.post(LICHNGAY_URL, headers=HEADERS, data=payload, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find_all(class_='table1')
        text = clean_content(content)
        return text
    except Exception as e:
        return f"Lỗi khi lấy dữ liệu: {e}"

def fetch_stories():
    global _stories_cache
    if _stories_cache is not None:
        return _stories_cache
    
    try:
        response = requests.get(STORIES_URL, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('article')
        full_text = article.get_text() if article else soup.get_text()
        
        pattern = r'(\d+\.\s)(?=[A-ZÀ-ỹ])'
        matches = list(re.finditer(pattern, full_text))
        
        stories = []
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i+1].start() if i+1 < len(matches) else len(full_text)
            story = full_text[start:end].strip()
            if len(story) > 100:
                stories.append(story)
        
        _stories_cache = stories[:23]
        return _stories_cache
    except Exception as e:
        logger.error(f"Lỗi fetch_stories: {e}")
        return []

def fetch_news(limit=10):
    try:
        response = requests.get(NEWS_URL, timeout=15)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.text)
        channel = root.find('channel')
        news = []
        if channel is not None:
            items = channel.findall('item')[:limit]
            for item in items:
                title = item.find('title')
                link = item.find('link')
                pub_date = item.find('pubDate')
                news.append({
                    "title": title.text if title is not None else "Không có tiêu đề",
                    "link": link.text if link is not None else "",
                    "pubDate": pub_date.text if pub_date is not None else ""
                })
        return news
    except Exception as e:
        return [{"error": f"Lỗi: {e}"}]

@mcp.tool()
def ngay_nay_nam_xua(opt: str = "TODAY") -> dict:
    """
    📜 Trả về sự kiện 'Ngày này năm xưa' (nguồn: lichngaytot.com)
    - opt: "TODAY" | "YESTERDAY" | "TOMORROW"
    """
    opt = opt.upper().strip()
    if opt not in ["TODAY", "YESTERDAY", "TOMORROW"]:
        opt = "TODAY"
    text = fetch_history(opt)
    logger.info(f"Lấy sự kiện {opt}: {text[:60]}...")
    return {"success": True, "option": opt, "events": text}

@mcp.tool()
def tin_tuc_vnexpress(limit: int = 10) -> dict:
    """
    📰 Lấy tin tức mới nhất từ VNExpress
    - limit: Số lượng tin (mặc định: 10, tối đa: 50)
    """
    limit = min(max(1, limit), 50)
    news = fetch_news(limit)
    result = f"📰 Tin mới nhất từ VNExpress (Top {len(news)}):\n\n"
    for i, item in enumerate(news, 1):
        if "error" in item:
            return {"success": False, "content": item["error"]}
        result += f"{i}. {item['title']}\n"
        result += f"   🔗 {item['link']}\n"
        if item['pubDate']:
            result += f"   📅 {item['pubDate']}\n"
        result += "\n"
    logger.info(f"Lấy {len(news)} tin mới nhất")
    return {"success": True, "content": result}

@mcp.tool()
def truyen_ngu_ngon() -> dict:
    """
    📖 Trả về một câu chuyện ngắn ngẫu nhiên từ 23 câu chuyện
    """
    stories = fetch_stories()
    if not stories:
        return {"success": False, "content": "Không tìm thấy câu chuyện nào."}
    
    story = random.choice(stories)
    logger.info(f"Trả về câu chuyện ({len(story)} ký tự)")
    return {"success": True, "content": f"📖 Câu chuyện:\n\n{story}"}

if __name__ == "__main__":
    mcp.run(transport="stdio")