import requests
from collections import defaultdict

# Pexels API密钥
API_KEY = 'dESvTyqCMdAFgmvWMP1N9d4rOoCWyfE3d52PFleYdrZlz0MUBjrFHbFg'

def get_search_results(query):
    """获取搜索结果"""
    headers = {
        'Authorization': API_KEY,
    }
    
    url = f'https://api.pexels.com/v1/search'
    params = {
        'query': query,
        'per_page': 15,  # 获取更多结果来分析
        'size': 'large'  # 尝试获取大尺寸图片
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        total_results = data.get('total_results', 0)
        
        # 收集所有图片的描述和颜色
        descriptions = []
        colors = defaultdict(int)
        resolutions = defaultdict(int)
        
        if 'photos' in data:
            for photo in data['photos']:
                if 'alt' in photo and photo['alt']:
                    descriptions.append(photo['alt'])
                if 'avg_color' in photo:
                    colors[photo['avg_color']] += 1
                if 'width' in photo and 'height' in photo:
                    resolution = f"{photo['width']}x{photo['height']}"
                    resolutions[resolution] += 1
        
        print(f"\nResults for: {query}")
        print(f"Total available images: {total_results}")
        
        if descriptions:
            print("\nSample image descriptions:")
            for desc in descriptions[:5]:  # 只显示前5个描述
                print(f"- {desc}")
        
        if resolutions:
            print("\nCommon resolutions:")
            for res, count in sorted(resolutions.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"- {res}: {count} images")
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def main():
    # 测试更多的分类关键词
    test_queries = [
        "modern interior",
        "minimalist home",
        "luxury apartment",
        "scandinavian design",
        "industrial style",
        "contemporary kitchen"
    ]
    
    for query in test_queries:
        get_search_results(query)
        print("-" * 50)

if __name__ == "__main__":
    main()
