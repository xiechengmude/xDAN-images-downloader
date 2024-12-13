"""
Pexels下载器配置文件
包含所有下载器需要的配置参数，包括路径、API设置、下载设置等
"""
import os
import yaml

# 基础路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pexels模块的根目录
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')      # 下载文件保存的根目录

# API请求头配置
HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',  # 请求语言设置
    'Secret-Key': 'dESvTyqCMdAFgmvWMP1N9d4rOoCWyfE3d52PFleYdrZlz0MUBjrFHbFg'  # API密钥
}

# 下载配置参数
PER_PAGE = 10                  # 每页返回的图片/视频数量
MAX_RETRIES = 3               # 下载失败时的最大重试次数
RETRY_DELAY = 2               # 重试之间的等待时间（秒）
MAX_PAGES_PER_CATEGORY = 1    # 每个分类最多下载的页数，防止过度请求

# API端点配置
ENDPOINTS = {
    'photos': 'https://www.pexels.com/en-us/api/v3/search/photos',  # 图片搜索API端点
    'videos': 'https://www.pexels.com/en-us/api/v3/search/videos'   # 视频搜索API端点
}

# 分辨率配置
RESOLUTION_FILTERS = {
    '4K': {
        'min_width': 3840,
        'min_height': 2160
    },
    '8K': {
        'min_width': 7680,
        'min_height': 4320
    }
}

# 搜索参数默认值
DEFAULT_SEARCH_PARAMS = {
    'page': '1',              # 页码，从1开始
    'per_page': str(PER_PAGE),# 每页数量
    'orientation': 'all',     # 图片方向：all-所有方向
    'size': 'large',         # 图片尺寸：large-获取最大尺寸
    'color': 'all',          # 颜色筛选：all-所有颜色
    'sort': 'popular',       # 排序方式：popular-按热度排序
    'seo_tags': 'true'       # 是否返回SEO标签
}

# 分类配置
# 可以在这里直接定义分类和关键词，也可以从categories.yaml文件加载
CATEGORIES = {
    'interior': [
        'modern interior'  # 测试关键词
    ]
}

# 从YAML文件加载分类配置
def load_categories():
    """从YAML文件加载分类配置"""
    categories_file = os.path.join(BASE_DIR, 'categories.yaml')
    if os.path.exists(categories_file):
        with open(categories_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return CATEGORIES

# 加载分类配置
CATEGORIES = load_categories()
