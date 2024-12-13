import os
import json
import urllib.parse
import requests
import pandas as pd
from urllib.parse import unquote

def get_filename_from_url(url):
    # 从content-disposition或URL中提取文件名
    try:
        disposition = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('response-content-disposition', [None])[0]
        if disposition:
            filename = disposition.split('filename=')[1]
            filename = unquote(filename)  # URL解码
            return filename
        else:
            return os.path.basename(urllib.parse.urlparse(url).path)
    except:
        return os.path.basename(urllib.parse.urlparse(url).path)

def download_image(url, folder):
    if not url or pd.isna(url):  # 检查URL是否为空或NaN
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
    results = []
    for _, row in df.iterrows():
        material_img = download_image(row['物料图片'], 'images/material')
        case_img = download_image(row['案例图片'], 'images/case')
        
        result = {
            'name': row['物料名称'],
            'category': row['分类'],
            'material_image': material_img,
            'case_image': case_img
        }
        results.append(result)
        print(f"Processed: {row['物料名称']}")
    return results

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
