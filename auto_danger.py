
import requests
from lxml import etree
from universal_storage_v2 import save
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0'
}
firsturl='https://fanqienovel.com/page/7582506140836039704'
resp=requests.get(url=firsturl,headers=headers)
resp.encoding='utf-8'
htmlStr=resp.text
htmlDoc=etree.HTML(htmlStr)
print(htmlDoc)
a_s=htmlDoc.xpath('//*[contains(@class, "chapter")]//div[contains(@class, "chapter-item")]//a')
print(a_s)

chapters=[]
baseurl='https://fanqienovel.com'
for a in a_s:
    title=a.xpath('string()').strip()
    link=a.xpath('@href')[0]
    full_url=baseurl + link if not link.startswith('http') else link
    chapters.append({
        'title':title,
        'link':full_url
    })


# ========== 新增：使用自动化存储保存数据 ==========
# 保存章节列表（不修改原有代码）
if chapters:
    result = save(
        data=chapters,  # 章节列表数据
        target_formats=['excel', 'csv', 'json', 'txt'],  # 保存为多种格式
        filename="fanqie_chapters"  # 文件名
    )
    
    print("\n" + "="*50)
    print("数据已保存！")
    print(f"原始文件: {result['raw_files'][0]}")
    print(f"转换文件: {result['converted_files']}")
    print("="*50)