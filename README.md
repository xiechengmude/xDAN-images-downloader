# Pexels 图片爬虫

这是一个用于下载 Pexels 网站室内图片的爬虫程序。该程序使用 Pexels 官方 API 进行图片获取，确保合法且高效。

## 功能特点

- 使用 Pexels 官方 API
- 支持批量下载高质量图片
- 自动创建下载目录
- 图片验证和错误处理
- 下载进度显示
- 自动重命名并保存图片

## 使用前准备

1. 注册 Pexels API
   - 访问 https://www.pexels.com/api/
   - 注册并获取 API key

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量
   - 复制 `.env.example` 为 `.env`
   - 在 `.env` 文件中填入你的 API key
   ```
   PEXELS_API_KEY=your_api_key_here
   DOWNLOAD_PATH=./downloads
   ```

## 使用方法

运行爬虫程序：
```bash
python pexels_crawler.py
```

## 注意事项

- 请遵守 Pexels 的使用条款和API限制
- 建议设置适当的下载间隔，避免频繁请求
- 下载的图片将保存在 `downloads` 目录下
- 图片文件名格式：`图片ID_摄影师名_时间戳.jpg`

## 代码结构

- `pexels_crawler.py`: 主程序文件
- `requirements.txt`: 依赖包列表
- `.env.example`: 环境变量示例文件
- `downloads/`: 图片下载目录
