"""
测试Pexels API支持的分辨率参数
"""
import requests
from loguru import logger
import json

def test_size_params():
    """测试不同的size参数"""
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Secret-Key': 'H2jk9uKnhRmL6WPwh89zBezWvr'
    }
    
    # 测试不同的size参数
    size_options = ['large', 'medium', 'small', 'all']
    
    for size in size_options:
        params = {
            'query': 'landscape',
            'per_page': '5',
            'size': size
        }
        
        url = 'https://www.pexels.com/en-us/api/v3/search/photos'
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"\nTesting size parameter: {size}")
            logger.info(f"Response structure: {json.dumps(data, indent=2)}")
            
            # 打印每张图片的分辨率
            for item in data['data']:
                try:
                    width = item['attributes']['image']['width']
                    height = item['attributes']['image']['height']
                    logger.info(f"Resolution: {width}x{height}")
                except KeyError as e:
                    logger.error(f"Key not found: {e}")
        else:
            logger.error(f"Error with size={size}: {response.status_code}")

if __name__ == '__main__':
    test_size_params()
