import requests
from bs4 import BeautifulSoup
import re


def extract_wechat_images(url):
    """
    从微信公众号文章中提取所有图片和SVG链接

    参数:
        url (str): 微信公众号文章链接

    返回:
        list: 包含所有图片和SVG链接的列表
    """
    try:
        # 获取文章内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有img标签
        img_tags = soup.find_all('img')
        img_links = [img.get('data-src') or img.get('src') for img in img_tags if img.get('data-src') or img.get('src')]

        # 查找所有svg标签（通常是内联SVG）
        svg_tags = soup.find_all('svg')
        svg_links = []

        # 查找可能包含SVG链接的其他元素
        for element in soup.find_all(style=re.compile(r'background-image\s*:\s*url\(.*\.svg\)')):
            style = element.get('style')
            svg_url = re.search(r'url\((.*?\.svg)\)', style)
            if svg_url:
                svg_links.append(svg_url.group(1))

        # 查找所有可能包含图片链接的元素
        for element in soup.find_all(style=re.compile(r'background-image\s*:\s*url\(.*?\)')):
            style = element.get('style')
            img_url = re.search(r'url\((.*?)\)', style)
            if img_url:
                img_links.append(img_url.group(1))

        # 合并并去重
        all_links = list(set(img_links + svg_links))

        # 过滤掉空值和相对路径
        filtered_links = [
            link if link.startswith(('http://', 'https://'))
            else f"https:{link}" if link.startswith('//')
            else None
            for link in all_links if link
        ]

        return [link for link in filtered_links if link]

    except Exception as e:
        print(f"Error occurred: {e}")
        return []


# 示例使用
if __name__ == "__main__":
    wechat_url = input("请输入微信公众号文章链接: ")
    images = extract_wechat_images(wechat_url)
    print("\n提取到的图片和SVG链接:")
    for i, img in enumerate(images, 1):
        print(f"{i}. {img}")
