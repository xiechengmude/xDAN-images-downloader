      from requests.compat import unquote
from loguru import logger
from tqdm import tqdm
import time
import os
import re
import requests
import warnings
warnings.filterwarnings('ignore')

def request(url, params=None, data=None, json=None):
    """
    发送HTTP请求，自动处理重试
    """
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Secret-Key': 'H2jk9uKnhRmL6WPwh89zBezWvr'
    }
    method = 'post' if (data or json) else 'get'
    script = f'requests.{method}(url,headers=headers,params=params,data=data,json=json)'
    while True:
        try:
            res = eval(script)
            if res.status_code == 200 or res.status_code == 302 or res.status_code == 401:
                break
            else:
                raise Exception(res.status_code)
        except Exception as ec:
            log = ec.__str__() + '（请忽略，正在自动重试...）'
            logger.debug(log)
            time.sleep(1)
    return res

def search(type, keyword, page=1):
    """
    搜索图片或视频
    type: 'photos' 或 'videos'
    keyword: 搜索关键词
    page: 页码
    """
    if type == 'photos':
        url = 'https://www.pexels.com/en-us/api/v3/search/photos'
    if type == 'videos':
        url = 'https://www.pexels.com/en-us/api/v3/search/videos'
    params = {
        'page': str(page),
        'per_page': '24',
        'query': keyword,
        'orientation': 'all',
        'size': 'all',
        'color': 'all',
        'sort': 'popular',
        'seo_tags': 'true'
    }
    res = request(url, params=params)
    res_json = res.json()
    data = res_json['data']
    total_pages = res_json['pagination']['total_pages']
    return data, total_pages

def download(type, save_path, url):
    """
    下载文件
    type: 'photos' 或 'videos'
    save_path: 保存路径
    url: 下载链接
    """
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Secret-Key': 'H2jk9uKnhRmL6WPwh89zBezWvr'
    }
    res = requests.get(url, headers=headers, stream=True)
    if type == 'photos':
        file_name = save_path.split('/')[-1]
        with open(save_path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024):
                f.write(chunk)
    if type == 'videos':
        file_name = re.search('filename=(.*)', res.url).group(1)
        file_name = re.sub('\\|/|:|\*|\?|"|<|>|\||/', '', file_name)
        save_path += unquote(file_name)
        file_size = int(res.headers.get('Content-length', 0))
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
        with open(save_path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024):
                f.write(chunk)    
                progress_bar.update(len(chunk))
        progress_bar.close()    
    return file_name

def main(keywords, type='photos'):
    """
    主函数：下载指定关键词的图片或视频
    keywords: 关键词列表
    type: 'photos' 或 'videos'
    """
    directory = 'download'
    for keyword in keywords:
        for page in range(1, 335):  # 最大页数限制
            logger.debug(f'正在下载 "{keyword}" 第{page}页')
            data, total_pages = search(type, keyword, page=page)
            
            if data == [] and total_pages == 1:
                logger.warning(f'找不到与 "{keyword}" 相关结果')
                break
                
            if page >= total_pages:
                break
                
            # 创建保存目录
            save_dir = f'{directory}/{type}/{keyword}'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 下载当前页的所有内容
            for index, item in enumerate(data):
                length = len(data)
                # 获取下载链接
                download_link = item['attributes']['image']['download_link'] if type == 'photos' else item['attributes']['video']['download_link']
                # 获取文件名
                file_name = re.search('dl=(.*)&', download_link).group(1) if type == 'photos' else ''
                file_name = unquote(file_name)
                save_path = f'{save_dir}/{file_name}'
                
                # 如果文件已存在则跳过
                if os.path.exists(save_path): 
                    continue
                    
                try:
                    file_name = download(type, save_path, download_link)
                    logger.success(f'下载成功（{index+1}/{length}）：{file_name}')
                except Exception as ec:
                    logger.error(f'下载失败（{index+1}/{length}）：{str(ec)}')
                    continue
                    
    logger.success('下载完毕！')

if __name__ == '__main__':
    # 设置要下载的关键词和类型
    keywords = ['Interior design', 'indoor']  # 搜索关键词列表
    main(keywords, type='photos')  # 下载图片，如果要下载视频改为 type='videos'