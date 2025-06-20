#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：axiongtest 
@File    ：main.py
@Author  ：fengzhengxiong
@Date    ：2025/6/10 11:25 
'''

# main.py
from agent import OrchestratorAgent
from tools import WeatherTool, NewsTool


def main():
    # 1. 初始化所有可用的工具
    available_tools = [
        WeatherTool(),
        NewsTool()
    ]

    # 2. 创建总管Agent实例，并把工具“注册”给它
    ai_assistant = OrchestratorAgent(tools=available_tools)

    # 3. 定义用户请求
    user_request = "帮我生成一份今天的简报。我需要知道北京的天气，以及关于人工智能的最新新闻。"

    # 4. 运行Agent
    ai_assistant.run(user_request)


if __name__ == "__main__":
    main()