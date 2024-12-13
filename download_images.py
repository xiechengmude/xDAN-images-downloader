import os
import json
import urllib.parse
import requests
import pandas as pd
from urllib.parse import unquote
import concurrent.futures
import multiprocessing
from tqdm import tqdm
import psutil

def get_optimal_workers():
    """根据CPU使用情况动态确定最优的工作进程数"""
    cpu_count = multiprocessing.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 根据CPU使用率动态调整
    if cpu_percent < 50:
        return max(cpu_count - 1, 1)  # 至少保留1个工作进程
    elif cpu_percent < 75:
        return max(cpu_count // 2, 1)
    else:
        return max(cpu_count // 4, 1)

def get_filename_from_url(url):
    try:
        disposition = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('response-content-disposition', [None])[0]
        if disposition:
            filename = disposition.split('filename=')[1]
            filename = unquote(filename)
            return filename
        else:
            return os.path.basename(urllib.parse.urlparse(url).path)
    except:
        return os.path.basename(urllib.parse.urlparse(url).path)

def download_single_image(args):
    """单个图片下载函数"""
    url, folder = args
    if not url or pd.isna(url):
        return None
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = get_filename_from_url(url)
            filepath = os.path.join(folder, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return filename
        return None
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None

def process_materials(df):
    """并发处理所有材料的下载任务"""
    results = []
    
    # 准备下载任务
    material_tasks = [(row['物料图片'], 'images/material') for _, row in df.iterrows()]
    case_tasks = [(row['案例图片'], 'images/case') for _, row in df.iterrows()]
    all_tasks = material_tasks + case_tasks
    
    # 获取最优的工作进程数
    workers = get_optimal_workers()
    print(f"Using {workers} worker processes for downloading...")
    
    # 使用进度条显示下载进度
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # 创建进度条
        with tqdm(total=len(all_tasks), desc="Downloading images") as pbar:
            # 提交所有下载任务
            future_to_url = {executor.submit(download_single_image, task): task for task in all_tasks}
            
            # 处理完成的任务
            for future in concurrent.futures.as_completed(future_to_url):
                url, folder = future_to_url[future]
                try:
                    filename = future.result()
                    if filename:
                        # 记录成功的下载
                        results.append({
                            'url': url,
                            'filename': filename,
                            'folder': folder
                        })
                except Exception as e:
                    print(f"Download failed for {url}: {str(e)}")
                finally:
                    pbar.update(1)
    
    # 整理结果
    final_results = []
    for idx, row in df.iterrows():
        material_img = next((r['filename'] for r in results if r['url'] == row['物料图片']), None)
        case_img = next((r['filename'] for r in results if r['url'] == row['案例图片']), None)
        
        result = {
            'name': row['物料名称'],
            'category': row['分类'],
            'material_image': material_img,
            'case_image': case_img
        }
        final_results.append(result)
    
    return final_results

def save_to_jsonl(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    # 确保目录存在
    os.makedirs('images/material', exist_ok=True)
    os.makedirs('images/case', exist_ok=True)
    
    # 读取Excel文件
    df = pd.read_excel('部分物料数据.xlsx')
    
    # 处理数据并下载图片
    results = process_materials(df)
    
    # 保存结果到JSONL文件
    save_to_jsonl(results, 'materials.jsonl')
    print("Processing completed. Check materials.jsonl for results.")
