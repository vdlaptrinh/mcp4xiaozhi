from mcp.server.fastmcp import FastMCP
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import logging

logger = logging.getLogger("TinMoiNhat")

if sys.platform == "win32":
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

mcp = FastMCP("TinMoiNhat")

RSS_URL = "https://vnexpress.net/rss/tin-moi-nhat.rss"

def fetch_news(limit: int = 10):
    try:
        response = requests.get(RSS_URL, timeout=15)
        response.encoding = 'utf-8'
        
        root = ET.fromstring(response.text)
        channel = root.find('channel')
        
        news = []
        items = channel.findall('item')[:limit] if channel is not None else []
        
        for item in items:
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            description = item.find('description')
            
            news.append({
                "title": title.text if title is not None else "Không có tiêu đề",
                "link": link.text if link is not None else "",
                "pubDate": pub_date.text if pub_date is not None else "",
                "description": description.text if description is not None else ""
            })
        
        return news
    except Exception as e:
        return [{"error": f"Lỗi: {e}"}]

@mcp.tool()
def tin_moi_nhat(limit: int = 10) -> dict:
    """
    📰 Lấy tin tức mới nhất từ VNExpress (nguồn: vnexpress.net/rss)
    
    - limit: Số lượng tin muốn lấy (mặc định: 10, tối đa: 50)
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

if __name__ == "__main__":
    mcp.run(transport="stdio")