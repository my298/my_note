import requests
from lxml import etree
from universal_storage_v2 import auto_save  # 只导入这一个函数

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 存储所有章节内容
all_chapters = []
# 92030
for i in range(91693,91700 ):
    url = f'https://www.shuzhaige.com/douluodalu/{i}.html'
    print(f"============第{i-91692}章==========")
    
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    htmlDoc = etree.HTML(resp.text)
    ps = htmlDoc.xpath('//p[normalize-space(text())]')
    
    # 收集内容
    chapter_text = '\n'.join([p.xpath('string()').strip() for p in ps])
    print(chapter_text[:100] + "...")  # 只打印前100字
    
    # 存储章节数据
    chapter_data = {
        "chapter_num": i - 91692,
        "url": url,
        "content": chapter_text,
        "paragraphs": len(ps)
    }
    
    # ========== 一行代码自动保存！ ==========
    auto_save(chapter_data)  # 自动保存，自动命名，自动选择格式
    
print("爬取完成！数据已自动保存到 crawler_data/ 目录")