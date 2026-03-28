"""
独立调用脚本 - 不修改原始爬虫代码
"""
import requests
from lxml import etree
from universal_storage_v2 import save  # 导入存储工具

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0'
}

# 91693--92029
for i in range(91693, 91700):
    url = f'https://www.shuzhaige.com/douluodalu/{i}.html'
    print(f"============第{i-91692}章==========")
    
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    htmlStr = resp.text
    htmlDoc = etree.HTML(htmlStr)
    ps = htmlDoc.xpath('//p[normalize-space(text())]')
    
    # # ========== 原有代码保持不变 ==========
    # with open('novle.txt', 'a', encoding='utf-8') as f:
    #     for p in ps:
    #         content = p.xpath('string()').strip()
    #         print(content)
    #         f.write(content + '\n')
    
    # ========== 新增：同时使用自动化存储 ==========
    # 收集本章节所有内容
    chapter_content = []
    for p in ps:
        content = p.xpath('string()').strip()
        if content:
            chapter_content.append(content)
    
    # 保存为多种格式（不影响原有保存）
    if chapter_content:
        save(
            data='\n'.join(chapter_content),  # 章节文本
            target_formats=['json', 'csv'],   # 额外保存为JSON和CSV
            filename=f"chapter_{i-91692}",     # 每章单独保存
        )

print("\n爬取完成！")
print("原有文件: novle.txt")
print("新增文件: crawler_data/raw/ 和 crawler_data/converted/")