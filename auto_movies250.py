import requests
from lxml import etree
from universal_storage_v2 import save  # 导入存储工具

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
}

all_movies = []

for i in range(10):
    url = f'https://movie.douban.com/top250?start={i*25}&filter='
    resp = requests.get(url=url, headers=headers)
    resp.encoding = 'utf-8'
    htmlStr = resp.text
    htmldoc = etree.HTML(htmlStr)
    
    names = htmldoc.xpath("//*[contains(@class,'hd')]/a/span[1]/text()")
    infos = htmldoc.xpath("//*[contains(@class,'bd')]/p[1]/text()[2]")
    
    for name, info in zip(names, infos):
        parts = info.split("/")
        if len(parts) >= 3:
            year = parts[0].strip()
            country = parts[1].strip()
            movietype = parts[2].strip()
            moviesData = {
                '电影名': name,
                '年份': year,
                '国家': country,
                '类型': movietype,
            }
            all_movies.append(moviesData)

# ========== 使用万能存储工具保存 ==========
# 方式1：保存为多种格式
result = save(
    data=all_movies,  # 电影数据列表
    target_formats=['excel', 'csv', 'json', 'txt'],  # 同时保存4种格式
    filename="movies250",  # 文件名
    # 注意：因为数据已经是字典列表，不需要 custom_config
)

print("=" * 50)
print("保存完成！")
print(f"原始数据文件: {result['raw_files'][0]}")
print(f"转换文件: {result['converted_files']}")
print("=" * 50)

# 方式2：如果只想保存Excel（和原来一样）
# save(all_movies, target_formats=['excel'], filename="movies250")

# 方式3：如果想保留原来的代码风格
# df = pd.DataFrame(all_movies)
# df.to_excel('movies250.xlsx', index=False)
# 但这样只能保存一种格式