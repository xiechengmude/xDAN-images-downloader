from pexels.downloader import PexelsDownloader
from loguru import logger
import sys

# 配置日志输出
logger.remove()  # 移除默认的日志处理器
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "download.log",
    rotation="100 MB",
    retention="1 week",
    level="DEBUG"
)

def main():
    # 创建下载器实例
    downloader = PexelsDownloader()
    
    # 方式1：使用预定义的分类下载（从config.py中读取）
    downloader.download_all_categories(content_type='photos')
    
    # 方式2：自定义下载特定关键词的图片
    categories = {
        'nature': ['forest', 'mountain', 'ocean'],
        'city': ['modern city', 'night city'],
        'food': ['healthy food', 'dessert']
    }
    
    for category, keywords in categories.items():
        try:
            downloader.process_category(category, keywords, content_type='photos')
        except Exception as e:
            logger.error(f"Error processing category {category}: {str(e)}")
            continue

if __name__ == '__main__':
    main()
