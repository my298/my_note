<!-- # 自动存储
## 第一步：编写universal_storage_v2
## 第二步：怎么使用
### 第一步：导入from universal_storage_v2 import save
### 第二步：爬取数据，将数据放在一个数组里面
### 第三步：引用
```
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
```

## 实战
### 案例一：爬取电影数据
```
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
```
### 对于这个案例：
#### 1.1 循环遍历多个变量
```
for name, info in zip(names, infos):
```

#### 1.2 保存
```
result = save(
    data=all_movies,  # 电影数据列表
    target_formats=['excel', 'csv', 'json', 'txt'],  # 同时保存4种格式
    filename="movies250",  # 文件名
    # 注意：因为数据已经是字典列表，不需要 custom_config
)

```
* target_formats :转换的目标格式
  
### 案例二：爬取小说数据
```
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
``` -->

# UniversalStorageV2 万能数据存储转换系统使用指南

## 📦 概述

UniversalStorageV2 是一个强大的数据存储转换工具，能够自动识别任意格式的输入数据，保存原始格式，并同时转换到多种目标格式（Excel、CSV、JSON、TXT、HTML、XML、YAML、Markdown等）。

---

## 🚀 核心特性

- ✅ **自动格式识别**：自动检测输入数据格式（字典、列表、DataFrame、JSON字符串、HTML/XML等）
- ✅ **原始数据保存**：保留数据原始格式，存入 `raw/` 目录
- ✅ **多格式转换**：一次性转换为多种目标格式
- ✅ **智能文件名生成**：自动生成或自定义文件名
- ✅ **目录结构清晰**：`raw/` 存放原始数据，`converted/` 存放转换后数据

---

## 📁 目录结构

```
crawler_data/
├── raw/              # 原始数据（原样保存）
│   ├── movies250.json
│   └── movies250.html
└── converted/        # 转换后的数据
    ├── movies250.xlsx
    ├── movies250.csv
    ├── movies250.json
    └── movies250.txt
```

---

## 📖 安装与导入

```python
# 将 universal_storage_v2.py 放在项目目录下
from universal_storage_v2 import save, save_raw, convert_file, storage
```

---

## 🔧 主要用法

### 1️⃣ 基础用法：保存为多种格式

```python
from universal_storage_v2 import save

# 数据可以是字典、列表、DataFrame等
data = [
    {"name": "阿甘正传", "year": 1994, "rating": 9.5},
    {"name": "肖申克的救赎", "year": 1994, "rating": 9.7}
]

# 同时保存为 Excel、CSV、JSON、TXT
result = save(
    data=data,
    target_formats=['excel', 'csv', 'json', 'txt'],
    filename="movies_top"
)

# 返回结果包含所有保存的文件路径
print(f"原始文件: {result['raw_files'][0]}")
print(f"转换文件: {result['converted_files']}")
```

**输出示例**：
```
原始文件: crawler_data/raw/movies_top.json
转换文件: ['crawler_data/converted/movies_top.xlsx', 
           'crawler_data/converted/movies_top.csv',
           'crawler_data/converted/movies_top.json',
           'crawler_data/converted/movies_top.txt']
```

---

### 2️⃣ 只保存原始格式

```python
# 只保存原始格式，不进行转换
result = save(
    data=all_movies,
    filename="movies_raw"
)
# 数据会保存为自动识别的原始格式（如 JSON）
```

---

### 3️⃣ 自动生成文件名

如果不指定 `filename`，系统会自动生成文件名：

```python
# 自动生成文件名（基于时间戳+内容哈希）
result = save(data=all_movies, target_formats=['excel'])
# 文件名示例: data_20240115_143022_a1b2c3d4.xlsx
```

---

### 4️⃣ 处理爬虫数据（完整示例）

```python
import requests
from lxml import etree
from universal_storage_v2 import save

headers = {'User-Agent': 'Mozilla/5.0...'}
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

# 一键保存为多种格式
result = save(
    data=all_movies,
    target_formats=['excel', 'csv', 'json', 'txt'],
    filename="douban_top250"
)

print(f"✅ 保存成功！共 {len(all_movies)} 条数据")
```

---

### 5️⃣ 按分类分别保存

```python
import pandas as pd
from universal_storage_v2 import save

df = pd.DataFrame(all_movies)

# 获取所有类型
all_genres = set()
for types in df['类型'].str.split():
    all_genres.update(types)

# 为每个类型保存独立文件
for genre in sorted(all_genres):
    genre_movies = df[df['类型'].str.contains(genre)]
    
    if not genre_movies.empty:
        save(
            data=genre_movies.to_dict('records'),
            target_formats=['excel', 'csv', 'json'],
            filename=f"movies_{genre}"
        )
        print(f"✅ 保存 {genre}类 共 {len(genre_movies)} 部电影")
```

---

### 6️⃣ 转换已有文件

```python
from universal_storage_v2 import convert_file

# 将已有文件转换为其他格式
result = convert_file(
    source_file="crawler_data/raw/movies.json",  # 源文件路径
    target_format="excel",                        # 目标格式
    output_filename="movies_from_json"            # 输出文件名（可选）
)
print(f"转换完成: {result}")
```

---

### 7️⃣ 使用自定义配置（HTML提取）

```python
from universal_storage_v2 import save

html_content = "<html><body><p>第一段</p><p>第二段</p></body></html>"

# 自定义提取规则
result = save(
    data=html_content,
    source_format='html_string',  # 指定原始格式
    target_formats=['txt', 'json'],
    custom_config={
        'selector': '//p/text()',      # XPath 选择器
        'extract_text_only': True      # 只提取文本
    }
)
```

---

## 🎯 支持的格式

### 输入格式（自动识别）
| 格式 | 说明 |
|------|------|
| `dict` | Python 字典 |
| `list` | Python 列表 |
| `list_of_dicts` | 字典组成的列表 |
| `dataframe` | pandas DataFrame |
| `json_string` | JSON 字符串 |
| `html_string` | HTML 字符串 |
| `xml_string` | XML 字符串 |
| `text_string` | 纯文本字符串 |
| `lxml_element` | lxml 元素对象 |
| `beautifulsoup` | BeautifulSoup 对象 |

### 输出格式
| 格式 | 扩展名 | 说明 |
|------|--------|------|
| `json` | .json | JSON 文件 |
| `csv` | .csv | CSV 文件（UTF-8-BOM） |
| `excel` | .xlsx | Excel 文件 |
| `txt` | .txt | 纯文本文件 |
| `html` | .html | HTML 文件 |
| `xml` | .xml | XML 文件 |
| `yaml` | .yaml | YAML 文件 |
| `markdown` | .md | Markdown 文件 |
| `parquet` | .parquet | Parquet 列式存储 |
| `pickle` | .pkl | Python pickle 序列化 |

---

## ⚙️ 返回值说明

`save()` 方法返回一个字典：

```python
{
    "filename": "movies250",              # 原始文件名
    "source_format": "list_of_dicts",     # 自动识别的源格式
    "raw_files": [                         # 原始文件路径列表
        "crawler_data/raw/movies250.json"
    ],
    "converted_files": [                   # 转换文件路径列表
        "crawler_data/converted/movies250.xlsx",
        "crawler_data/converted/movies250.csv",
        "crawler_data/converted/movies250.json"
    ],
    "error_excel": "错误信息"              # 如果转换失败，会有错误键
}
```

---

## ⚠️ 注意事项

### 1. **数据类型限制**
- 复杂对象（如自定义类）会被转换为字符串
- 循环引用对象会导致转换失败

### 2. **文件编码**
- 所有文本文件使用 **UTF-8** 编码
- CSV 文件使用 **UTF-8-BOM** 解决 Excel 中文乱码

### 3. **路径问题**
- 默认保存目录为 `crawler_data/`（当前工作目录下）
- 会自动创建 `raw/` 和 `converted/` 子目录

### 4. **自定义配置**
- `custom_config` 主要用于 HTML/XML 数据提取
- 常用配置：`selector`（XPath选择器）、`extract_text_only`（是否只提取文本）

### 5. **性能考虑**
- 大文件（>100MB）建议使用流式处理
- 批量转换时注意内存占用

### 6. **格式冲突**
- 如果 `target_formats` 包含源格式，不会重复转换
- 例如源格式为 JSON，目标格式包含 JSON，则只保存原始 JSON

---

## 🛠️ 自定义存储目录

```python
from universal_storage_v2 import UniversalStorageV2

# 自定义存储目录
storage = UniversalStorageV2(data_dir="my_data")

# 使用自定义实例
result = storage.save(
    data=all_movies,
    target_formats=['excel', 'json'],
    filename="my_movies"
)
```

---

## 📊 实际应用场景

### 场景1：爬虫数据多格式备份
```python
# 爬取数据后立即保存为多种格式，方便后续使用
save(
    data=all_articles,
    target_formats=['json', 'csv', 'excel'],
    filename=f"articles_{date}"
)
```

### 场景2：数据清洗中间结果
```python
# 保存清洗前后的数据对比
save(raw_data, target_formats=['json'], filename="step1_raw")
cleaned_data = clean_data(raw_data)
save(cleaned_data, target_formats=['excel', 'csv'], filename="step2_cleaned")
```

### 场景3：按条件分片保存
```python
# 按年份分片保存
for year in range(2000, 2024):
    year_data = [m for m in movies if m['year'] == year]
    if year_data:
        save(year_data, target_formats=['excel'], filename=f"movies_{year}")
```

---

## 🔍 调试技巧

查看已保存的所有文件：
```python
from universal_storage_v2 import storage

# 列出所有文件
files = storage.list_files()
print(f"原始文件: {files['raw']}")
print(f"转换文件: {files['converted']}")
```

查看当前配置：
```python
print(f"数据目录: {storage.data_dir}")
print(f"支持格式: {storage.SUPPORTED_FORMATS}")
```

---

## 📝 总结

UniversalStorageV2 让数据存储变得极其简单：
- **一行代码**实现多格式保存
- **自动识别**输入格式，无需手动指定
- **灵活扩展**，支持自定义转换规则
- **结构化存储**，便于文件管理

无论是爬虫项目、数据分析还是日常开发，这个工具都能大大简化数据持久化的工作。


## 相关代码
### [危险病患] auto_danger.py
### [豆瓣电影250] auto_movies250.py
### [豆瓣电影250分类] movie_auto.py
### [小说爬取] auto_novel.py
