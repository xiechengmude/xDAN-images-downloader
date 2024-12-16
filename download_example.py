"""
Pexels下载器使用示例
展示了几种不同的下载方式和配置方法
"""
from pexels.downloader import PexelsDownloader
from pexels import config
from loguru import logger
import sys
import os

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

def example_1_simple():
    """示例1：最简单的使用方式"""
    logger.info("开始示例1：简单下载")
    downloader = PexelsDownloader()
    
    # 下载单个关键词的图片
    keywords = ['interior']
    downloader.process_category('interior', keywords, content_type='photos')

def example_2_multiple_keywords():
    """示例2：下载多个关键词的图片"""
    logger.info("开始示例2：多关键词下载")
    downloader = PexelsDownloader()
    
    # 定义多个关键词
    categories = {
        'nature': ['forest', 'mountain', 'ocean'],
        'city': ['modern city', 'night city'],
        'food': ['healthy food', 'dessert']
    }
    
    # 下载每个分类的图片
    for category, keywords in categories.items():
        try:
            logger.info(f"开始下载分类: {category}")
            downloader.process_category(category, keywords, content_type='photos')
        except Exception as e:
            logger.error(f"下载分类 {category} 时出错: {str(e)}")
            continue

def example_3_photos_and_videos():
    """示例3：同时下载图片和视频"""
    logger.info("开始示例3：图片和视频下载")
    downloader = PexelsDownloader()
    
    # 定义要下载的关键词
    keywords = ['coffee shop']
    category = 'business'
    
    # 下载图片
    logger.info("下载图片...")
    downloader.process_category(category, keywords, content_type='photos')
    
    # 下载视频
    logger.info("下载视频...")
    downloader.process_category(category, keywords, content_type='videos')

def example_4_with_config():
    """示例4：使用配置文件中的分类"""
    logger.info("开始示例4：使用配置文件")
    downloader = PexelsDownloader()
    
    # 使用配置文件中定义的分类
    categories = config.CATEGORIES
    
    for category, keywords in categories.items():
        try:
            logger.info(f"开始下载配置文件中的分类: {category}")
            downloader.process_category(category, keywords, content_type='photos')
        except Exception as e:
            logger.error(f"下载分类 {category} 时出错: {str(e)}")
            continue

def example_5_custom_settings():
    """示例5：自定义下载设置"""
    logger.info("开始示例5：自定义设置")
    downloader = PexelsDownloader()
    
    # 修改配置
    config.PER_PAGE = 300                 # 每页30张图片
    config.MAX_PAGES_PER_CATEGORY = 20000    # 每个分类下载2页
    config.DEFAULT_SEARCH_PARAMS.update({
        'orientation': 'landscape',       # 只下载横向图片
        'size': 'large'                  # 只下载大尺寸图片
    })
    
    # 下载图片
    keywords = ['interior']
    downloader.process_category('interior', keywords, content_type='photos')

def main():
    """主函数：运行所有示例"""
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 设置日志
    setup_logger()
    
    # 运行示例
    logger.info("=== 开始运行下载示例 ===")
    
    try:
        # 示例1：简单下载
        example_1_simple()
        
        # 示例2：多关键词下载
        # example_2_multiple_keywords()
        
        # 示例3：图片和视频下载
        # example_3_photos_and_videos()
        
        # 示例4：使用配置文件
        # example_4_with_config()
        
        # 示例5：自定义设置
        # example_5_custom_settings()
        
    except KeyboardInterrupt:
        logger.warning("用户中断下载")
    except Exception as e:
        logger.error(f"运行示例时出错: {str(e)}")
    finally:
        logger.info("=== 下载示例结束 ===")

if __name__ == '__main__':
    main()
