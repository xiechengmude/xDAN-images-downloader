"""
Main script to run the Pexels downloader
"""
from loguru import logger
from downloader import PexelsDownloader

def main():
    # Initialize downloader
    downloader = PexelsDownloader()
    
    # Define keywords for search
    keywords = ['Interior design', 'indoor']
    
    try:
        # Start downloading
        downloader.download_by_keywords(keywords, content_type='photos')
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")

if __name__ == '__main__':
    main()
