from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import sys
import logging
import re
def load_lich_lam_viec():
    global _lich_cache
    if _lich_cache is not None:
        return _lich_cache
    
    try:
        import pandas as pd
        df = pd.read_excel(LICH_LICH_VIEC_FILE)
        
        events = []
        current_date = None
        current_time = None
        
        for _, row in df.iterrows():
            thu_ngay = row.get('THỨ NGÀY', '')
            
            if pd.notna(thu_ngay) and str(thu_ngay).strip():
                current_date = str(thu_ngay).replace('\n', ' ')
                current_time = str(row.get('THỜI GIAN', '')) if pd.notna(row.get('THỜI GIAN')) else ''
            else:
                current_time = str(row.get('THỜI GIAN', '')) if pd.notna(row.get('THỜI GIAN')) else ''
            
            noi_dung = str(row.get('NỘI DUNG CÔNG VIỆC', '')) if pd.notna(row.get('NỘI DUNG CÔNG VIỆC')) else ''
            chu_tri = str(row.get('CHỦ TRÌ', '')) if pd.notna(row.get('CHỦ TRÌ')) else ''
            dia_diem = str(row.get('ĐỊA ĐIỂM', '')) if pd.notna(row.get('ĐỊA ĐIỂM')) else ''
            thanh_phan = str(row.get('THÀNH PHẦN', '')) if pd.notna(row.get('THÀNH PHẦN')) else ''
            
            if noi_dung:
                events.append({
                    'thu_ngay': current_date,
                    'thoi_gian': current_time,
                    'noi_dung': noi_dung,
                    'chu_tri': chu_tri,
                    'dia_diem': dia_diem,
                    'thanh_phan': thanh_phan
                })
        
        _lich_cache = events
        return events
    except Exception as e:
        logger.error(f"Lỗi load_lich_lam_viec: {e}")
        return []

def search_lich_cong_tac(query):
    events = load_lich_lam_viec()
    query_lower = query.lower()
    
    results = []
    
    for event in events:
        match = False
        thu_ngay = event.get('thu_ngay', '') or ''
        thoi_gian = event.get('thoi_gian', '') or ''
        noi_dung = event.get('noi_dung', '').lower()
        chu_tri = event.get('chu_tri', '').lower()
        dia_diem = event.get('dia_diem', '') or ''
        thanh_phan = event.get('thanh_phan', '') or ''
        
        if query_lower in thu_ngay.lower():
            match = True
        elif query_lower in ['thứ hai', 'thứ 2', 'hai']:
            if 'hai' in thu_ngay.lower():
                match = True
        elif query_lower in ['thứ ba', 'thứ 3', 'ba']:
            if 'ba' in thu_ngay.lower():
                match = True
        elif query_lower in ['thứ tư', 'thứ 4', 'tư']:
            if 'tư' in thu_ngay.lower():
                match = True
        elif query_lower in ['thứ năm', 'thứ 5', 'năm']:
            if 'năm' in thu_ngay.lower():
                match = True
        elif query_lower in ['thứ sáu', 'thứ 6', 'sáu']:
            if 'sáu' in thu_ngay.lower():
                match = True
        elif query_lower in ['thứ bảy', 'thứ 7', 'bảy']:
            if 'bảy' in thu_ngay.lower():
                match = True
        elif query_lower in ['chủ nhật', 'cn']:
            if 'cn' in thu_ngay.lower():
                match = True
        elif any(x in query_lower for x in ['ngày', '/', '-']):
            if query_lower.split()[0] in thu_ngay.lower():
                match = True
        elif query_lower in chu_tri:
            match = True
        elif query_lower in noi_dung:
            match = True
        elif query_lower in thanh_phan.lower():
            match = True
        
        if match:
            results.append(event)
    
    return results

def format_lich_cong_tac(events):
    if not events:
        return "Không tìm thấy lịch công tác phù hợp."
    
    result = f"Tìm thấy {len(events)} sự kiện:\n\n"
    
    current_thu = None
    for event in events:
        thu_ngay = event.get('thu_ngay', '') or ''
        if thu_ngay != current_thu:
            result += f"{'='*50}\n"
            result += f"📅 {thu_ngay}\n"
            result += f"{'='*50}\n"
            current_thu = thu_ngay
        
        thoi_gian = event.get('thoi_gian', '')
        noi_dung = event.get('noi_dung', '')
        chu_tri = event.get('chu_tri', '')
        dia_diem = event.get('dia_diem', '')
        thanh_phan = event.get('thanh_phan', '')
        
        result += f"⏰ {thoi_gian}\n"
        result += f"📋 {noi_dung}\n"
        if chu_tri:
            result += f"👤 Chủ trì: {chu_tri}\n"
        if dia_diem:
            result += f"📍 Địa điểm: {dia_diem}\n"
        if thanh_phan:
            result += f"👥 Thành phần: {thanh_phan}\n"
        result += "\n"
    
    return result

LICH_LICH_VIEC_FILE = "lich_lam_viec.xlsx"
_lich_cache = None

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

@mcp.tool()
def lich_cong_tac(query: str = "") -> dict:
    """
    📅 Tra cứu lịch công tác, lịch làm việc từ file lich_lam_viec.xlsx
    
    Cách hỏi:
    - "lich cong tac thu hai" - Lịch thứ Hai
    - "lich ngay 22/4" - Lịch ngày 22/4
    - "hieu truong co lich gi" - Hỏi lịch của Hiệu trưởng
    - "họp" - Tìm các cuộc họp trong tuần
    - "toan bo lich" - Toàn bộ lịch tuần
    """
    if not query.strip():
        events = load_lich_lam_viec()
        return {"success": True, "content": format_lich_cong_tac(events)}
    
    events = search_lich_cong_tac(query)
    logger.info(f"Tìm kiếm lịch công tác: '{query}' - Kết quả: {len(events)}")
    return {"success": True, "content": format_lich_cong_tac(events)}

if __name__ == "__main__":
    mcp.run(transport="stdio")