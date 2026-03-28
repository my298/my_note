import requests
from lxml import etree
import pandas as pd
from universal_storage_v2 import save

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
}

all_movies = []

for i in range(10):
    url = f'https://movie.douban.com/top250?start={i*25}&filter='
    resp = requests.get(url=url, headers=headers)
    resp.encoding = 'utf-8'
    htmldoc = etree.HTML(resp.text)
    
    names = htmldoc.xpath("//*[contains(@class,'hd')]/a/span[1]/text()")
    infos = htmldoc.xpath("//*[contains(@class,'bd')]/p[1]/text()[2]")
    
    for name, info in zip(names, infos):
        parts = info.split("/")
        if len(parts) >= 3:
            all_movies.append({
                '电影名': name,
                '年份': parts[0].strip(),
                '国家': parts[1].strip(),
                '类型': parts[2].strip(),
            })

# 转换为DataFrame
df = pd.DataFrame(all_movies)

# ========== 按类型分类存储 ==========

# 方法1：每个类型保存为独立文件
# 获取所有类型（处理多个类型用空格分隔的情况）
all_genres = set()
for types in df['类型'].str.split():
    all_genres.update(types)  # 如果有多个类型，分别添加

print(f"共找到 {len(all_genres)} 种类型: {sorted(all_genres)}")

# 为每个类型保存独立文件
for genre in sorted(all_genres):
    # 筛选该类型的电影
    genre_movies = df[df['类型'].str.contains(genre)]
    
    if not genre_movies.empty:
        # 转换为字典列表并保存
        save(
            data=genre_movies.to_dict('records'),
            target_formats=['excel', 'csv', 'json'],  # 保存多种格式
            filename=f"movies_{genre}类"
        )
        print(f"已保存 {genre}类 共 {len(genre_movies)} 部电影")
