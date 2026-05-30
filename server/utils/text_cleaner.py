"""文本清洗工具"""
import re


def clean_text(text: str) -> str:
    """清洗文本：去除多余空白、特殊字符"""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def extract_price(text: str) -> float | None:
    """从文本中提取价格"""
    if not text:
        return None
    patterns = [
        r"(\d+(?:\.\d+)?)\s*元/月",
        r"(\d+(?:\.\d+)?)\s*元",
        r"月租[：:]?\s*(\d+(?:\.\d+)?)",
        r"租金[：:]?\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*/月",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None


def extract_area(text: str) -> str | None:
    """从文本中提取区域信息"""
    if not text:
        return None
    # 匹配常见区域格式
    patterns = [
        r"([一-龥]+区)",
        r"([一-龥]+县)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None
