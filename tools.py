#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：axiongtest 
@File    ：tools.py
@Author  ：fengzhengxiong
@Date    ：2025/6/10 11:25 
'''

# tools.py
import requests
import json
import os


# --- 抽象基类，定义所有工具的统一接口 ---
class Tool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, params: dict) -> str:
        raise NotImplementedError


# --- 具体工具 1: 天气工具 ---
class WeatherTool(Tool):
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="获取指定城市的实时天气。参数: {'city': '城市名称'}"
        )
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def execute(self, params: dict) -> str:
        city = params.get("city")
        if not city:
            return "错误: 未提供城市名称。"

        # 构建请求URL
        url = f"{self.base_url}?q={city}&appid={self.api_key}&units=metric&lang=zh_cn"
        try:
            response = requests.get(url)
            response.raise_for_status()  # 如果请求失败则抛出异常
            data = response.json()

            # 格式化输出
            result = (
                f"{data['name']}的天气情况: "
                f"{data['weather'][0]['description']}, "
                f"温度: {data['main']['temp']}°C, "
                f"体感温度: {data['main']['feels_like']}°C, "
                f"湿度: {data['main']['humidity']}%"
            )
            return result
        except requests.exceptions.RequestException as e:
            return f"错误: 调用天气API失败 - {e}"
        except KeyError:
            return f"错误: 未找到城市 '{city}' 的天气数据。"


# --- 具体工具 2: 新闻工具 ---
class NewsTool(Tool):
    def __init__(self):
        super().__init__(
            name="get_news",
            description="获取关于特定主题的最新新闻头条。参数: {'topic': '主题关键词'}"
        )
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def execute(self, params: dict) -> str:
        topic = params.get("topic")
        if not topic:
            return "错误: 未提供新闻主题。"

        url = f"{self.base_url}?q={topic}&apiKey={self.api_key}&language=zh&pageSize=5"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            articles = data.get("articles", [])
            if not articles:
                return f"未找到关于 '{topic}' 的新闻。"

            # 格式化输出
            headlines = [f"{i + 1}. {article['title']}" for i, article in enumerate(articles)]
            return f"关于 '{topic}' 的最新新闻头条:\n" + "\n".join(headlines)
        except requests.exceptions.RequestException as e:
            return f"错误: 调用新闻API失败 - {e}"