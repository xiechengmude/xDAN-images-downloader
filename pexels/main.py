"""
Main script to run the Pexels downloader
"""
from loguru import logger
from .downloader import PexelsDownloader
from .category_manager import CategoryManager
import argparse

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='Pexels Downloader')
    parser.add_argument('--type', choices=['photos', 'videos'], default='photos',
                      help='Content type to download (photos or videos)')
    parser.add_argument('--category', help='Specific category to download (optional)')
    parser.add_argument('--update-categories', action='store_true',
                      help='Update categories before downloading')
    parser.add_argument('--discover', nargs='+',
                      help='Discover categories based on provided keywords')
    args = parser.parse_args()
    
    try:
        # 处理分类更新
        if args.update_categories or args.discover:
            category_manager = CategoryManager()
            if args.discover:
                logger.info(f"Discovering categories for keywords: {args.discover}")
                category_manager.update_categories(args.discover)
            else:
                logger.info("Updating categories with default keywords")
                category_manager.update_categories()
        
        # 初始化下载器
        downloader = PexelsDownloader()
        
        # 处理下载
        if args.category:
            # 下载特定分类
            from .config import CATEGORIES
            if args.category in CATEGORIES:
                logger.info(f"Downloading category: {args.category}")
                downloader.process_category(args.category, CATEGORIES[args.category], args.type)
            else:
                logger.error(f"Category {args.category} not found in configuration")
        else:
            # 下载所有分类
            logger.info("Downloading all categories")
            downloader.download_all_categories(args.type)
            
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
    except Exception as e:
        logger.error(f"Process failed: {str(e)}")
    else:
        logger.success("Process completed successfully!")

if __name__ == '__main__':
    main()
