from pexels.downloader import PexelsDownloader
from pexels import config
from loguru import logger

def test_4k_download():
    # 修改配置
    config.PER_PAGE = 10
    config.MAX_PAGES_PER_CATEGORY = 1
    
    # 初始化下载器
    downloader = PexelsDownloader()
    
    # 设置关键词
    keywords = ['landscape', 'mountain', 'nature']
    
    logger.info("Starting to download 4K images...")
    
    # 下载4K分辨率的图片
    downloader.process_category(
        category='4k_test',
        keywords=keywords,
        content_type='photos',
        resolution_filter='4K'
    )
    
    logger.info("Download completed!")

if __name__ == "__main__":
    test_4k_download()
