"""
万能数据存储转换系统
支持任何格式的输入，自动识别，保存原始格式，转换到任何目标格式
"""

import json
import csv
import pandas as pd
from pathlib import Path
from typing import Any, Optional, Dict, List, Union
from datetime import datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import yaml
import pickle
import hashlib


class UniversalStorageV2:
    """
    万能存储转换器 V2
    特性：
    - 自动识别任何输入数据的格式
    - 保存原始数据（原样）
    - 转换到任何目标格式
    - 支持自定义转换规则
    """
    
    # 支持的格式
    SUPPORTED_FORMATS = {
        'json', 'csv', 'txt', 'html', 'xml', 'yaml', 'pickle', 
        'excel', 'parquet', 'markdown', 'list', 'dict', 'dataframe'
    }
    
    def __init__(self, data_dir: str = "crawler_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.raw_dir = self.data_dir / "raw"
        self.converted_dir = self.data_dir / "converted"
        self.raw_dir.mkdir(exist_ok=True)
        self.converted_dir.mkdir(exist_ok=True)
        
        # 注册转换器
        self._converters = {
            'json': self._to_json,
            'csv': self._to_csv,
            'txt': self._to_text,
            'html': self._to_html,
            'xml': self._to_xml,
            'yaml': self._to_yaml,
            'pickle': self._to_pickle,
            'excel': self._to_excel,
            'parquet': self._to_parquet,
            'markdown': self._to_markdown,
        }
    
    def save(self, data: Any, 
             filename: Optional[str] = None,
             source_format: Optional[str] = None,
             target_formats: Optional[Union[str, List[str]]] = None,
             custom_config: Optional[Dict] = None) -> Dict[str, str]:
        """
        智能保存数据
        
        :param data: 任何格式的数据
        :param filename: 文件名（不提供则自动生成）
        :param source_format: 原始格式（不提供则自动检测）
        :param target_formats: 目标格式，可以是单个格式或格式列表
        :param custom_config: 自定义转换配置
        :return: 保存的文件路径字典
        """
        # 自动生成文件名
        if filename is None:
            filename = self._auto_filename(data)
        
        # 自动检测原始格式
        if source_format is None:
            source_format = self._detect_format(data)
        
        result = {
            "filename": filename,
            "source_format": source_format,
            "raw_files": [],
            "converted_files": []
        }
        
        # 1. 保存原始数据
        raw_path = self._save_raw(data, filename, source_format)
        result["raw_files"].append(raw_path)
        
        # 2. 转换并保存到目标格式
        if target_formats:
            if isinstance(target_formats, str):
                target_formats = [target_formats]
            
            for target_format in target_formats:
                if target_format.lower() != source_format.lower():
                    try:
                        converted_data = self._convert(data, source_format, target_format, custom_config)
                        converted_path = self._save_converted(converted_data, filename, target_format)
                        result["converted_files"].append(converted_path)
                    except Exception as e:
                        result[f"error_{target_format}"] = str(e)
        
        return result
    
    def _detect_format(self, data: Any) -> str:
        """自动检测数据格式"""
        # 1. 检查特殊类型
        if isinstance(data, pd.DataFrame):
            return 'dataframe'
        
        if isinstance(data, (list, tuple)):
            if data and all(isinstance(item, dict) for item in data):
                return 'list_of_dicts'
            return 'list'
        
        if isinstance(data, dict):
            return 'dict'
        
        # 2. 检查字符串内容
        if isinstance(data, str):
            # 尝试 JSON
            try:
                json.loads(data)
                return 'json_string'
            except:
                pass
            
            # 尝试 XML/HTML
            data_stripped = data.strip()
            if data_stripped.startswith('<'):
                if data_stripped.startswith('<?xml'):
                    return 'xml_string'
                else:
                    return 'html_string'
            
            return 'text_string'
        
        # 3. lxml 元素
        if hasattr(data, 'xpath'):
            return 'lxml_element'
        
        # 4. BeautifulSoup 对象
        if hasattr(data, 'find_all'):
            return 'beautifulsoup'
        
        # 5. 其他
        return 'unknown'
    
    def _save_raw(self, data: Any, filename: str, format: str) -> str:
        """保存原始数据"""
        # 根据格式选择保存方式
        if format in ['json', 'json_string']:
            filepath = self.raw_dir / f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                if format == 'json_string':
                    f.write(data)
                else:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        
        elif format in ['csv', 'dataframe']:
            filepath = self.raw_dir / f"{filename}.csv"
            df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        elif format in ['html_string', 'xml_string']:
            filepath = self.raw_dir / f"{filename}.{'html' if 'html' in format else 'xml'}"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
        
        elif format in ['lxml_element', 'beautifulsoup']:
            filepath = self.raw_dir / f"{filename}.html"
            if hasattr(data, 'xpath'):
                # lxml 元素
                content = ET.tostring(data, encoding='unicode') if hasattr(data, 'tag') else str(data)
            else:
                # BeautifulSoup
                content = str(data)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        elif format in ['list', 'list_of_dicts', 'dict']:
            filepath = self.raw_dir / f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        else:  # text_string 或其他
            filepath = self.raw_dir / f"{filename}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        return str(filepath)
    
    def _convert(self, data: Any, source_format: str, target_format: str, 
                 config: Optional[Dict] = None) -> Any:
        """转换数据格式"""
        # 先标准化为内部格式
        normalized = self._normalize(data, source_format, config)
        
        # 再转换为目标格式
        converter = self._converters.get(target_format)
        if not converter:
            raise ValueError(f"不支持的转换格式: {target_format}")
        
        return converter(normalized, config)
    
    def _normalize(self, data: Any, source_format: str, config: Optional[Dict] = None) -> Dict:
        """
        标准化为字典格式
        所有格式都先转为统一的字典格式，便于后续转换
        """
        if source_format in ['json', 'json_string', 'dict', 'list_of_dicts']:
            if isinstance(data, str):
                return json.loads(data)
            return data
        
        elif source_format in ['csv', 'dataframe']:
            if isinstance(data, pd.DataFrame):
                return data.to_dict(orient='records')
            return pd.DataFrame(data).to_dict(orient='records')
        
        elif source_format in ['html_string', 'lxml_element', 'beautifulsoup']:
            # 提取文本内容
            return self._extract_content(data, source_format, config)
        
        elif source_format == 'xml_string':
            return self._parse_xml(data)
        
        elif source_format == 'text_string':
            return {"content": data}
        
        else:
            # 尝试直接转换
            try:
                return {"data": str(data)}
            except:
                return {"raw": str(data)}
    
    def _extract_content(self, data: Any, source_format: str, config: Optional[Dict] = None) -> Dict:
        """从 HTML/XML 中提取内容"""
        config = config or {}
        
        # 获取选择器
        selector = config.get('selector', '//p[normalize-space(text())]')
        extract_text_only = config.get('extract_text_only', True)
        
        if source_format == 'lxml_element':
            # lxml 元素
            if hasattr(data, 'xpath'):
                elements = data.xpath(selector)
                if extract_text_only:
                    content = [elem.xpath('string()').strip() for elem in elements if elem.xpath('string()').strip()]
                else:
                    content = [ET.tostring(elem, encoding='unicode') for elem in elements]
                return {"content": content, "count": len(content)}
        
        elif source_format == 'beautifulsoup':
            # BeautifulSoup
            from bs4 import BeautifulSoup
            soup = data if isinstance(data, BeautifulSoup) else BeautifulSoup(data, 'html.parser')
            # 简化处理，提取所有文本
            content = soup.get_text().strip().split('\n')
            content = [line.strip() for line in content if line.strip()]
            return {"content": content, "count": len(content)}
        
        elif source_format == 'html_string':
            from lxml import html
            tree = html.fromstring(data)
            elements = tree.xpath(selector)
            if extract_text_only:
                content = [elem.xpath('string()').strip() for elem in elements if elem.xpath('string()').strip()]
            else:
                content = [html.tostring(elem, encoding='unicode') for elem in elements]
            return {"content": content, "count": len(content)}
        
        return {"content": [], "count": 0}
    
    def _parse_xml(self, xml_string: str) -> Dict:
        """解析 XML"""
        try:
            root = ET.fromstring(xml_string)
            return self._xml_to_dict(root)
        except:
            return {"xml": xml_string}
    
    def _xml_to_dict(self, element):
        """XML 转字典"""
        result = {}
        for child in element:
            if len(child):
                result[child.tag] = self._xml_to_dict(child)
            else:
                result[child.tag] = child.text
        return result or element.text
    
    def _to_json(self, data: Any, config: Optional[Dict] = None) -> Any:
        """转换为 JSON"""
        return data
    
    def _to_csv(self, data: Any, config: Optional[Dict] = None) -> pd.DataFrame:
        """转换为 CSV (DataFrame)"""
        if isinstance(data, pd.DataFrame):
            return data
        
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return pd.DataFrame(data)
        
        if isinstance(data, dict):
            return pd.DataFrame([data])
        
        return pd.DataFrame({"content": [str(data)]})
    
    def _to_text(self, data: Any, config: Optional[Dict] = None) -> str:
        """转换为纯文本"""
        if isinstance(data, str):
            return data
        
        if isinstance(data, dict):
            # 尝试提取内容
            if 'content' in data:
                content = data['content']
                if isinstance(content, list):
                    return '\n'.join([str(c) for c in content])
                return str(content)
            
            # 递归提取
            return self._dict_to_text(data)
        
        if isinstance(data, list):
            return '\n'.join([self._to_text(item) for item in data])
        
        return str(data)
    
    def _dict_to_text(self, d: dict, indent: int = 0) -> str:
        """字典转文本"""
        lines = []
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{' ' * indent}{key}:")
                lines.append(self._dict_to_text(value, indent + 2))
            elif isinstance(value, list):
                lines.append(f"{' ' * indent}{key}:")
                for item in value:
                    lines.append(f"{' ' * (indent + 2)}- {item}")
            else:
                lines.append(f"{' ' * indent}{key}: {value}")
        return '\n'.join(lines)
    
    def _to_html(self, data: Any, config: Optional[Dict] = None) -> str:
        """转换为 HTML"""
        text = self._to_text(data)
        return f"<html><body><pre>{text}</pre></body></html>"
    
    def _to_xml(self, data: Any, config: Optional[Dict] = None) -> str:
        """转换为 XML"""
        if isinstance(data, dict):
            root = ET.Element("root")
            self._dict_to_xml(data, root)
            return ET.tostring(root, encoding='unicode')
        return f"<root>{data}</root>"
    
    def _dict_to_xml(self, d: dict, parent):
        """字典转 XML"""
        for key, value in d.items():
            elem = ET.SubElement(parent, key)
            if isinstance(value, dict):
                self._dict_to_xml(value, elem)
            else:
                elem.text = str(value)
    
    def _to_yaml(self, data: Any, config: Optional[Dict] = None) -> str:
        """转换为 YAML"""
        return yaml.dump(data, allow_unicode=True)
    
    def _to_pickle(self, data: Any, config: Optional[Dict] = None) -> bytes:
        """转换为 Pickle"""
        return pickle.dumps(data)
    
    def _to_excel(self, data: Any, config: Optional[Dict] = None) -> pd.DataFrame:
        """转换为 Excel"""
        return self._to_csv(data)
    
    def _to_parquet(self, data: Any, config: Optional[Dict] = None) -> pd.DataFrame:
        """转换为 Parquet"""
        return self._to_csv(data)
    
    def _to_markdown(self, data: Any, config: Optional[Dict] = None) -> str:
        """转换为 Markdown"""
        text = self._to_text(data)
        lines = text.split('\n')
        return '\n'.join([f"> {line}" if line else line for line in lines])
    
    def _save_converted(self, data: Any, filename: str, format: str) -> str:
        """保存转换后的数据"""
        if format == 'json':
            filepath = self.converted_dir / f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        elif format == 'csv':
            filepath = self.converted_dir / f"{filename}.csv"
            df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        elif format == 'excel':
            filepath = self.converted_dir / f"{filename}.xlsx"
            df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
            df.to_excel(filepath, index=False)
        
        elif format == 'parquet':
            filepath = self.converted_dir / f"{filename}.parquet"
            df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
            df.to_parquet(filepath)
        
        elif format == 'yaml':
            filepath = self.converted_dir / f"{filename}.yaml"
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)
        
        elif format == 'pickle':
            filepath = self.converted_dir / f"{filename}.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        
        elif format in ['html', 'xml', 'markdown', 'txt']:
            filepath = self.converted_dir / f"{filename}.{format}"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        else:
            filepath = self.converted_dir / f"{filename}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        return str(filepath)
    
    def _auto_filename(self, data: Any) -> str:
        """自动生成文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if isinstance(data, dict):
            if 'title' in data:
                return str(data['title'])[:30].replace('/', '_')
            elif 'name' in data:
                return str(data['name'])[:30].replace('/', '_')
        
        # 生成内容哈希
        data_str = str(data)[:100]
        hash_val = hashlib.md5(data_str.encode()).hexdigest()[:8]
        
        return f"data_{timestamp}_{hash_val}"
    
    def convert_file(self, source_file: str, target_format: str, 
                     output_filename: Optional[str] = None) -> str:
        """转换已有文件"""
        source_path = Path(source_file)
        if not source_path.exists():
            source_path = self.raw_dir / source_file
        
        if not source_path.exists():
            raise FileNotFoundError(f"找不到文件: {source_file}")
        
        # 读取文件
        data = self._read_file(source_path)
        
        # 检测格式
        source_format = self._detect_format(data)
        
        # 转换
        if output_filename is None:
            output_filename = source_path.stem
        
        converted_data = self._convert(data, source_format, target_format)
        return self._save_converted(converted_data, output_filename, target_format)
    
    def _read_file(self, filepath: Path) -> Any:
        """读取文件"""
        suffix = filepath.suffix.lower()
        
        if suffix == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        elif suffix == '.csv':
            return pd.read_csv(filepath)
        
        elif suffix in ['.html', '.htm']:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
    
    def list_files(self) -> Dict:
        """列出所有文件"""
        return {
            "raw": [f.name for f in self.raw_dir.glob("*")],
            "converted": [f.name for f in self.converted_dir.glob("*")]
        }


# 创建全局实例
storage = UniversalStorageV2()


# ========== 快捷函数 ==========

def save(data, target_formats=None, filename=None, custom_config=None):
    """
    保存数据到多个格式
    :param data: 任何格式的数据
    :param target_formats: 目标格式列表，如 ['txt', 'json', 'csv']
    :param filename: 文件名
    :param custom_config: 自定义配置，如 {'selector': '//p/text()'}
    """
    return storage.save(data, filename, target_formats=target_formats, custom_config=custom_config)


def save_raw(data, filename=None):
    """只保存原始格式"""
    return storage.save(data, filename)


def convert_file(source_file, target_format, output_filename=None):
    """转换已有文件"""
    return storage.convert_file(source_file, target_format, output_filename)


if __name__ == "__main__":
    print("万能数据存储转换系统 V2 已就绪！")
    print("\n支持的输入格式:")
    print("  - JSON/字典/列表")
    print("  - CSV/DataFrame")
    print("  - HTML/XML (字符串或lxml元素)")
    print("  - 纯文本")
    print("\n支持的输出格式:")
    print("  - json, csv, txt, html, xml, yaml")
    print("  - excel, parquet, markdown, pickle")