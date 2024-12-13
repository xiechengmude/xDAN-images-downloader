"""
Pexels下载器使用示例
支持命令行参数来指定下载选项
"""
from pexels.downloader import PexelsDownloader
from pexels import config
from loguru import logger
import sys
import os
import argparse

def setup_logger():
    """配置日志输出"""
    # 移除默认的日志处理器
    logger.remove()
    
    # 添加控制台输出，显示彩色日志
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 添加文件日志，按大小轮换
    os.makedirs("logs", exist_ok=True)
    logger.add(
        "logs/download.log",
        rotation="100 MB",    # 每个日志文件最大100MB
        retention="1 week",   # 保留一周的日志
        compression="zip",    # 压缩旧日志
        level="DEBUG"         # 记录所有级别的日志
    )

def download_images(resolution=None, category=None, keywords=None):
    """下载指定分辨率和类别的图片
    Args:
        resolution: 分辨率要求 ('4K' 或 '8K')
        category: 自定义分类名称
        keywords: 搜索关键词列表
    """
    downloader = PexelsDownloader()
    
    if not keywords:
        # 默认的搜索关键词
        categories = {
            'landscape': ['mountain landscape', 'aerial landscape', 'forest landscape'],
            'nature': ['wilderness', 'national park', 'scenic vista'],
            'architecture': ['modern architecture', 'skyscraper', 'cityscape'],
            'aerial': ['drone photography', 'aerial view', 'bird eye view']
        }
        
        # 如果指定了category，只下载该分类
        if category and category in categories:
            categories = {category: categories[category]}
        
        # 遍历每个分类下载图片
        for cat, kwords in categories.items():
            logger.info(f"下载分类 '{cat}' 的图片")
            downloader.process_category(
                category=cat,
                keywords=kwords,
                content_type='photos',
                resolution_filter=resolution
            )
    else:
        # 使用用户指定的关键词
        category = category or 'custom'
        logger.info(f"使用关键词 {keywords} 下载图片")
        downloader.process_category(
            category=category,
            keywords=keywords,
            content_type='photos',
            resolution_filter=resolution
        )

def main():
    """主函数：处理命令行参数并执行下载"""
    parser = argparse.ArgumentParser(description='Pexels图片下载工具')
    
    parser.add_argument('--resolution', '-r',
                      choices=['4K', '8K'],
                      help='指定下载的图片分辨率 (4K 或 8K)')
    
    parser.add_argument('--category', '-c',
                      choices=['landscape', 'nature', 'architecture', 'aerial'],
                      help='指定下载的图片分类')
    
    parser.add_argument('--keywords', '-k',
                      nargs='+',
                      help='指定搜索关键词，可以提供多个，用空格分隔')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logger()
    
    try:
        # 执行下载
        download_images(
            resolution=args.resolution,
            category=args.category,
            keywords=args.keywords
        )
    except KeyboardInterrupt:
        logger.warning("用户中断下载")
    except Exception as e:
        logger.error(f"下载出错: {str(e)}")
    finally:
        logger.info("下载完成")

if __name__ == '__main__':
    main()
