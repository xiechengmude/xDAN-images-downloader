#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pexels.category_manager import CategoryManager
from loguru import logger

def main():
    # 创建分类管理器实例
    manager = CategoryManager()
    
    # 定义基础关键词，这些关键词将用于发现更多相关分类
    base_keywords = [
        # 自然与风景
        'nature', 'landscape', 'mountains', 'ocean', 'forest', 'beach', 'sunset', 'sunrise',
        'waterfall', 'desert', 'sky', 'clouds', 'stars', 'northern lights', 'rainbow',
        
        # 动物与野生生物
        'animals', 'wildlife', 'birds', 'pets', 'cats', 'dogs', 'marine life', 'insects',
        'endangered species', 'farm animals', 'zoo animals',
        
        # 城市与建筑
        'city', 'architecture', 'buildings', 'skyline', 'street', 'urban', 'monuments',
        'bridges', 'historical buildings', 'modern buildings', 'castles', 'churches',
        
        # 人物与生活
        'people', 'portraits', 'family', 'children', 'elderly', 'couples', 'friends',
        'lifestyle', 'culture', 'traditions', 'festivals', 'celebrations',
        
        # 运动与活动
        'sports', 'fitness', 'yoga', 'dance', 'extreme sports', 'water sports',
        'winter sports', 'team sports', 'olympics', 'adventure',
        
        # 食物与饮品
        'food', 'drinks', 'cuisine', 'restaurants', 'cooking', 'baking', 'fruits',
        'vegetables', 'desserts', 'beverages', 'wine', 'coffee',
        
        # 艺术与创意
        'art', 'painting', 'sculpture', 'photography', 'digital art', 'street art',
        'illustrations', 'crafts', 'music', 'theater', 'dance performance',
        
        # 科技与创新
        'technology', 'computers', 'gadgets', 'robots', 'artificial intelligence',
        'space', 'science', 'innovation', 'future tech', 'virtual reality',
        
        # 商业与职场
        'business', 'office', 'workplace', 'startup', 'corporate', 'meeting',
        'presentation', 'teamwork', 'leadership', 'entrepreneurship',
        
        # 教育与学习
        'education', 'school', 'university', 'library', 'study', 'research',
        'laboratory', 'classroom', 'students', 'teachers',
        
        # 旅行与探险
        'travel', 'adventure', 'vacation', 'tourism', 'hotels', 'resorts',
        'camping', 'hiking', 'backpacking', 'road trip',
        
        # 季节与天气
        'spring', 'summer', 'autumn', 'winter', 'snow', 'rain', 'storm',
        'fog', 'sunshine', 'weather', 'seasons',
        
        # 交通与运输
        'transportation', 'cars', 'trains', 'planes', 'ships', 'bicycles',
        'motorcycles', 'public transport', 'traffic', 'space ships',
        
        # 环境与自然保护
        'environment', 'conservation', 'sustainability', 'renewable energy',
        'climate change', 'recycling', 'green living', 'eco friendly',
        
        # 健康与医疗
        'health', 'medical', 'hospital', 'healthcare', 'wellness', 'mental health',
        'fitness', 'meditation', 'spa', 'alternative medicine',
        
        # 时尚与美容
        'fashion', 'beauty', 'makeup', 'hair', 'skincare', 'accessories',
        'jewelry', 'clothing', 'models', 'fashion show',
        
        # 家居与园艺
        'home', 'garden', 'interior design', 'furniture', 'decoration', 'plants',
        'landscaping', 'home improvement', 'architecture', 'real estate',
        
        # 抽象与概念
        'abstract', 'concept', 'minimalism', 'pattern', 'texture', 'geometry',
        'colors', 'shapes', 'light', 'shadow', 'reflection',
        
        # 节日与庆典
        'holidays', 'christmas', 'new year', 'halloween', 'easter',
        'thanksgiving', 'birthday', 'wedding', 'party', 'celebration',
        
        # 情感与心情
        'emotions', 'happiness', 'love', 'sadness', 'anger', 'fear',
        'joy', 'peace', 'excitement', 'tranquility'
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
