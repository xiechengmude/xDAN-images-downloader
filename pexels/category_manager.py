"""
Category discovery and management module
"""
import os
import yaml
from loguru import logger
import requests
from typing import Dict, List, Set
from . import config

class CategoryManager:
    def __init__(self):
        """初始化分类管理器"""
        self.categories_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'categories.yaml')
        self.headers = config.HEADERS
        
    def load_categories(self) -> Dict:
        """加载现有分类"""
        if os.path.exists(self.categories_file):
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save_categories(self, categories: Dict) -> None:
        """保存分类到文件"""
        if not categories:
            logger.warning("No categories to save")
            return
            
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.categories_file), exist_ok=True)
            
            # 保存分类
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                yaml.dump(categories, f, allow_unicode=True, default_flow_style=False)
            
            logger.success(f"Categories saved to {self.categories_file}")
        except Exception as e:
            logger.error(f"Error saving categories: {str(e)}")
            raise
    
    def discover_categories(self, base_keywords: List[str]) -> Dict:
        """发现新的分类和关键词"""
        discovered = {}
        
        for base_keyword in base_keywords:
            logger.info(f"Discovering categories for: {base_keyword}")
            try:
                # 搜索基础关键词
                related_terms = self._search_related_terms(base_keyword)
                
                # 将基础关键词作为主分类
                category_name = base_keyword.lower().replace(' ', '_')
                if related_terms:
                    discovered[category_name] = sorted(list(related_terms))
                
            except Exception as e:
                logger.error(f"Error discovering categories for {base_keyword}: {str(e)}")
                continue
        
        return discovered
    
    def _search_related_terms(self, keyword: str) -> Set[str]:
        """搜索相关词"""
        url = config.ENDPOINTS['photos']
        params = {
            **config.DEFAULT_SEARCH_PARAMS,
            'query': keyword,
            'page': '1'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                # 从搜索结果中提取相关标签和建议
                related_terms = set()
                if 'tags' in data:
                    related_terms.update(tag['name'] for tag in data['tags'])
                if 'suggestions' in data:
                    related_terms.update(data['suggestions'])
                return related_terms
        except Exception as e:
            logger.warning(f"Error searching related terms for {keyword}: {str(e)}")
        return set()
    
    def _merge_categories(self, existing: Dict, new: Dict) -> Dict:
        """合并现有分类和新分类"""
        merged = existing.copy()
        
        for category, terms in new.items():
            if category in merged:
                # 如果分类已存在，添加新的关键词
                existing_terms = set(merged[category])
                existing_terms.update(terms)
                merged[category] = sorted(list(existing_terms))
            else:
                # 如果是新分类，直接添加
                merged[category] = sorted(terms)
        
        return merged
    
    def update_categories(self, base_keywords: List[str] = None):
        """更新分类文件"""
        if base_keywords is None:
            base_keywords = [
                'interior design', 'home decor', 'architecture',
                'room design', 'house design', 'office design'
            ]
        
        logger.info("Starting category discovery...")
        categories = self.discover_categories(base_keywords)
        self.save_categories(categories)
        logger.success("Category discovery and update completed!")
