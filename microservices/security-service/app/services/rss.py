import asyncio
import httpx
import feedparser
import logging
from typing import List
from app.schemas.payloads import RSSItem, RSSFeedResponse

logger = logging.getLogger(__name__)

class RSSService:
    RSS_SOURCES = [
        {"url": "https://blog.topsec.com.cn/feed/", "name": "天融信 (Topsec)"},
        {"url": "https://cert.360.cn/feed", "name": "360 CERT"},
        {"url": "https://blog.nsfocus.net/feed/", "name": "绿盟 (NSFOCUS)"},
    ]

    async def fetch_feed(self, client: httpx.AsyncClient, source: dict) -> List[RSSItem]:
        url = source["url"]
        name = source["name"]
        try:
            # Disable SSL verification is handled in client initialization
            response = await client.get(url, timeout=10.0, follow_redirects=True)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch RSS from {url}: status {response.status_code}")
                return []
            
            # 使用 feedparser 解析 XML 内容
            feed = feedparser.parse(response.text)
            items = []
            
            for entry in feed.entries[:10]: # 每个源只取前 10 条
                # 处理日期，feedparser 通常会提供 parsed_date 或 published
                published = entry.get("published", "")
                
                # 尝试提取描述，优先用 summary，没有则用 content
                description = entry.get("summary", "")
                if not description and "content" in entry:
                    # content 是个列表
                    description = entry.content[0].value if entry.content else ""
                
                # 简单清理一下 description 里的 HTML 标签（可选，这里先保留或简单截断）
                # 为了保持 API 响应整洁，可以截断
                if len(description) > 200:
                    description = description[:200] + "..."

                items.append(RSSItem(
                    title=entry.get("title", "No Title"),
                    link=entry.get("link", ""),
                    description=description,
                    published=published,
                    source=name
                ))
            return items

        except Exception as e:
            logger.error(f"Error fetching/parsing RSS from {url}: {str(e)}")
            return []

    async def get_security_news(self) -> RSSFeedResponse:
        """
        并发获取所有 RSS 源的新闻并聚合
        """
        all_items = []
        # Disable SSL verification globally for RSS client
        async with httpx.AsyncClient(verify=False) as client:
            tasks = [self.fetch_feed(client, source) for source in self.RSS_SOURCES]
            results = await asyncio.gather(*tasks)
            
            for res in results:
                all_items.extend(res)
        
        # 简单排序（如果 published 是标准格式最好，否则不做强排序，或者尽量保持各源顺序）
        # 这里不做复杂日期解析排序，直接返回聚合结果
        return RSSFeedResponse(items=all_items)
