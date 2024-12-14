#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pexels.category_manager import CategoryManager
from loguru import logger

def main():
    # 创建分类管理器实例
    manager = CategoryManager()
    
    # 定义基础关键词，这些关键词将用于发现更多相关分类
    base_keywords = [
        # 自然风景
        'nature landscape', 'mountain scenery', 'ocean views', 'forest landscape',
        'waterfall scenery', 'desert landscape', 'aerial landscape',
        
        # 城市景观
        'city landscape', 'urban architecture', 'cityscape', 'street photography',
        'night city', 'modern architecture', 'historical architecture',
        
        # 室内设计
        'interior design', 'modern interior', 'minimalist interior', 
        'luxury interior', 'industrial design', 'scandinavian interior',
        
        # 特定房间
        'living room design', 'kitchen interior', 'bedroom design', 
        'bathroom interior', 'office design', 'outdoor living',
        
        # 抽象和艺术
        'abstract art', 'modern art', 'digital art', 'minimalist art',
        'geometric patterns', 'artistic photography',
        
        # 生活方式
        'lifestyle photography', 'travel photography', 'food photography',
        'fashion photography', 'sports photography', 'wildlife photography'
    ]
    
    # 发现新的分类
    logger.info("开始发现新的分类...")
    categories = manager.discover_categories(base_keywords)
    
    # 保存更新后的分类
    logger.info("保存分类...")
    manager.save_categories(categories)
    
    logger.success("分类更新完成！")
    
if __name__ == '__main__':
    main()
