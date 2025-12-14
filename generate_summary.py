#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blog Summary Generator
扫描目录下所有markdown文件，提取v3标签信息，生成SUMMARY.md文件
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class BlogSummaryGenerator:
    def __init__(self):
        self.articles = []
        self.errors = []
        self.warnings = []
        
    def scan_directory(self, root_dir):
        """扫描目录下的所有markdown文件"""
        root_path = Path(root_dir)
        if not root_path.exists():
            raise ValueError(f"目录 {root_dir} 不存在")
            
        # 遍历所有目录，查找markdown文件
        for md_file in root_path.rglob("*.md"):
            # 跳过SUMMARY.md本身
            if md_file.name == "SUMMARY.md":
                continue
                
            article_info = self.parse_markdown_file(md_file)
            if article_info:
                self.articles.append(article_info)
    
    def parse_markdown_file(self, file_path):
        """解析单个markdown文件的v3标签"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 只检查前 100 行
            header_lines = lines[:100]
            content = ''.join(header_lines)
            
            v2_pattern = r'```\s*\n(?:v3\n)?(.*?)\n```'
            match = re.search(v2_pattern, content, re.DOTALL)
            
            if not match:
                self.errors.append(f"文件 {file_path} 缺少v3标签块")
                return None
                
            metadata_text = match.group(1)
            
            # 解析metadata
            metadata = self.parse_metadata(metadata_text, file_path)
            
            # 提取文章标题
            title = self.extract_title(lines)
            
            # 计算相对路径
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                rel_path = file_path
            
            article_info = {
                'file_path': str(rel_path).replace('\\', '/'),
                'title': title,
                'metadata': metadata,
                'category': metadata.get('category', ''),
                'created': metadata.get('created', ''),
                'published': metadata.get('published', ''),
                'tags': metadata.get('tags', []),
                'modified': metadata.get('modified', [])
            }
            
            return article_info
            
        except Exception as e:
            self.errors.append(f"解析文件 {file_path} 时出错: {str(e)}")
            return None
    
    def parse_metadata(self, metadata_text, file_path):
        """解析v3标签中的metadata"""
        metadata = {}
        lines = metadata_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 处理逗号分隔的字段（created, published, modified）
            if line.startswith('created,') or line.startswith('created:'):
                # created, 日期 或 created: 日期
                if ',' in line:
                    parts = line.split(',', 1)
                else:
                    parts = line.split(':', 1)
                if len(parts) >= 2:
                    metadata['created'] = parts[1].strip()
            elif line.startswith('published,') or line.startswith('published:'):
                # published, 日期 或 published: 日期
                if ',' in line:
                    parts = line.split(',', 1)
                else:
                    parts = line.split(':', 1)
                if len(parts) >= 2:
                    metadata['published'] = parts[1].strip()
            elif line.startswith('category:'):
                # category: 值
                parts = line.split(':', 1)
                if len(parts) >= 2:
                    metadata['category'] = parts[1].strip()
            elif line.startswith('tags:'):
                # tags: 标签列表
                parts = line.split(':', 1)
                if len(parts) >= 2:
                    tags_str = parts[1].strip()
                    metadata['tags'] = [tag.strip() for tag in tags_str.split(',')]
            elif line.startswith('modified,') or line.startswith('modified:'):
                # modified, 日期, 描述 或 modified: 日期, 描述
                if ',' in line:
                    parts = line.split(',', 1)
                else:
                    parts = line.split(':', 1)
                if len(parts) >= 2:
                    if 'modified' not in metadata:
                        metadata['modified'] = []
                    metadata['modified'].append(parts[1].strip())
        
        # 验证必需字段
        self.validate_metadata(metadata, file_path)
        
        return metadata
    
    def validate_metadata(self, metadata, file_path):
        """验证metadata字段"""
        required_fields = ['created', 'published', 'category']
        optional_fields = ['tags', 'modified']
        
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                self.errors.append(f"文件 {file_path} 缺少必需字段: {field}")
        
        # 检查可选字段
        for field in optional_fields:
            if field not in metadata:
                self.warnings.append(f"文件 {file_path} 缺少可选字段: {field}")
    
    def extract_title(self, lines):
        """提取文章标题"""
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return "无标题"
    
    def format_date(self, date_str):
        """格式化日期为YYYY-MM-DD格式"""
        try:
            # 处理ISO格式日期
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('+08:00', '+08:00'))
                return dt.strftime('%Y-%m-%d')
            return date_str  # 返回原始字符串
        except:
            return date_str
    
    def generate_filename(self, title, published_date):
        """根据标题和发布日期生成文件名"""
        date_part = self.format_date(published_date)
        # 将标题转换为URL友好的格式
        title_part = re.sub(r'[^\w\s-]', '', title)  # 移除特殊字符
        title_part = re.sub(r'\s+', '-', title_part)  # 空格替换为短横线
        title_part = title_part.lower()  # 转为小写
        return f"{date_part}-{title_part}"
    
    def generate_summary(self):
        """生成SUMMARY.md内容"""
        if not self.articles:
            return "# Blog Summary\n\n暂无文章"
        
        # 按发布日期排序（只包含有发布日期的文章）
        published_articles = [a for a in self.articles if a['published']]
        published_articles.sort(key=lambda x: x['published'] if x['published'] else '', reverse=True)
        
        output = []
        
        # 生成timeline部分
        output.append("timeline")
        output.append("")
        
        # 按年份分组（只包含有发布日期的文章）
        articles_by_year = defaultdict(list)
        for article in published_articles:
            try:
                # 只提取年份
                date_str = article['published'].strip()
                year = date_str[:4]
                articles_by_year[year].append(article)
            except:
                articles_by_year['未知'].append(article)
        
        # 按年份排序（未知放最后）
        years = [y for y in articles_by_year.keys() if y != '未知']
        years.sort(reverse=True)
        if '未知' in articles_by_year:
            years.append('未知')
        
        for year in years:
            output.append(f"-   {year}")
            for article in articles_by_year[year]:
                # 只提取日期部分用于链接标题
                date_str = article['published'].strip()
                date_formatted = date_str[:10]
                title = article['title']
                output.append(f"    -   [{date_formatted}-{title}](./{article['file_path']})")
            output.append("")
        
        output.append("---")
        output.append("")
        
        # 生成categories部分
        output.append("categories")
        output.append("")
        
        # 按category分组
        categories = defaultdict(list)
        for article in self.articles:
            category = article['category'] if article['category'] else '未分类'
            categories[category].append(article)
        
        # 定义category的显示名称和emoji
        category_display = {
            'wealth': 'wealth 别人恐惧我贪婪 😈',
            'spirit': 'spirit 努力追求自己的最好 🏃‍',
            'health': 'health 唱到 100 岁 🎤',
            'career': 'career 泪水打湿猪脚饭 💧',
            'reading': 'reading 爱看书的健健 📕',
            'nonsense': 'nonsense 🤔'
        }
        
        # 添加README（如果有）
        readme_article = next((a for a in self.articles if 'README.md' in a['file_path']), None)
        if readme_article:
            output.append(f"-   [Hello!](./{readme_article['file_path']})")
        
        for category in sorted(categories.keys()):
            display_name = category_display.get(category, f"{category} 📁")
            output.append(f"-   {display_name}")
            
            for article in categories[category]:
                if 'README.md' in article['file_path']:
                    continue  # README已经在上面处理了
                title = article['title']
                output.append(f"    -   [{title}](./{article['file_path']})")
            output.append("")
        
        output.append("---")
        output.append("")
        
        # 生成tags部分
        output.append("tags")
        output.append("")
        
        # 按tag分组
        tags = defaultdict(list)
        for article in self.articles:
            article_tags = article.get('tags', [])
            if article_tags:
                for tag in article_tags:
                    tags[tag].append(article)
        
        if tags:
            # 按标签名称排序
            for tag in sorted(tags.keys()):
                output.append(f"-   {tag}")
                # 按标题排序显示该标签下的文章
                tag_articles = sorted(tags[tag], key=lambda x: x['title'])
                for article in tag_articles:
                    title = article['title']
                    output.append(f"    -   [{title}](./{article['file_path']})")
                output.append("")
        else:
            output.append("<!-- 暂无标签  -->")
        
        return '\n'.join(output)
    
    def print_report(self):
        """打印处理报告"""
        print(f"扫描完成！")
        print(f"共找到 {len(self.articles)} 篇文章")
        
        if self.warnings:
            print(f"\n警告 ({len(self.warnings)} 个):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print(f"\n错误 ({len(self.errors)} 个):")
            for error in self.errors:
                print(f"  - {error}")
        
        if not self.errors and not self.warnings:
            print("所有文件格式正确！")


def main():
    parser = argparse.ArgumentParser(description='生成博客SUMMARY.md文件')
    parser.add_argument('--output', '-o', default='SUMMARY.md', help='输出文件名 (默认: SUMMARY.md)')
    parser.add_argument('--directory', '-d', default='.', help='扫描目录 (默认: 当前目录)')
    
    args = parser.parse_args()
    
    generator = BlogSummaryGenerator()
    
    try:
        generator.scan_directory(args.directory)
        summary_content = generator.generate_summary()
        
        # 写入文件
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        generator.print_report()
        print(f"\nSUMMARY.md 已生成: {args.output}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()