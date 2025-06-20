#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
@Project ：axiongtest
@File    ：agent.py
@Author  ：fengzhengxiong
@Date    ：2025/6/10 11:24
'''

# agent.py

import os
import json
# ！！！修改点 1: 导入 ZhipuAI 客户端
from zhipuai import ZhipuAI
from dotenv import load_dotenv
from tools import Tool  # 注意：这里我们不再需要导入 WeatherTool 和 NewsTool

# 加载环境变量
load_dotenv()


class OrchestratorAgent:
    def __init__(self, tools: list[Tool]):
        # ！！！修改点 2: 初始化 ZhipuAI 客户端
        self.client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
        self.tools = {tool.name: tool for tool in tools}
        # ！！！修改点 3: 使用智谱的模型，glm-4-flash性价比很高
        self.model = "glm-4-flash"

    def _get_tools_description(self) -> str:
        """生成工具描述，给LLM看"""
        return "\n".join([
            f"- {tool.name}: {tool.description}" for tool in self.tools.values()
        ])

    def _planner(self, user_query: str) -> list[dict]:
        """规划器：决定调用哪些工具"""
        tools_description = self._get_tools_description()

        # ！！！修改点 4: 为智谱AI模型调整Prompt，使其能输出稳定的JSON
        # 智谱模型对工具调用的理解方式更直接，我们可以使用更结构化的Prompt
        prompt = f"""
        你是一个智能调度助手。根据用户的请求，分析并决定需要调用哪些工具来完成任务。
        你必须以一个JSON数组的形式返回你的计划，每个对象包含'tool_name'和'params'。
        如果不需要调用工具，请返回一个空数组 []。

        [可用的工具]
        {tools_description}

        [用户请求]
        {user_query}

        [输出格式要求]
        严格按照以下JSON格式输出，不要包含任何其他文字或解释。
        {{
          "plan": [
            {{
              "tool_name": "工具名称",
              "params": {{ "参数名": "参数值" }}
            }}
          ]
        }}
        """

        # ！！！修改点 5: 修改API调用方式以匹配ZhipuAI SDK
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}  # 智谱同样支持JSON模式
        )

        plan_str = response.choices[0].message.content
        try:
            full_plan = json.loads(plan_str)
            return full_plan.get("plan", [])
        except (json.JSONDecodeError, KeyError) as e:
            print(f"解析计划失败: {e}\n原始输出: {plan_str}")
            return []

    def _executor(self, plan: list[dict]) -> dict:
        """执行器：根据计划调用工具"""
        # 这个方法无需修改，因为它不与LLM直接交互
        results = {}
        for step in plan:
            tool_name = step.get("tool_name")
            params = step.get("params")

            if tool_name in self.tools:
                print(f"  [执行中] ... 调用工具: {tool_name}，参数: {params}")
                tool = self.tools[tool_name]
                result = tool.execute(params)
                results[tool_name] = result
            else:
                results[tool_name] = f"错误: 未找到名为 '{tool_name}' 的工具。"
        return results

    def _synthesizer(self, user_query: str, execution_results: dict) -> str:
        """合成器：整合结果生成最终报告"""
        results_str = "\n\n".join([
            f"--- {tool_name} 的结果 ---\n{result}"
            for tool_name, result in execution_results.items()
        ])

        prompt = f"""
        你是一个专业的报告撰写助理。
        你的任务是根据用户的原始请求和各个工具的执行结果，生成一份通顺、连贯、友好的最终报告。
        请直接输出报告内容，不要说“好的，这是您的报告”等多余的话。

        [用户的原始请求]
        {user_query}

        [工具执行结果]
        {results_str}

        [你的最终报告]
        """

        # ！！！修改点 6: 修改API调用方式以匹配ZhipuAI SDK
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def run(self, user_query: str):
        """运行整个Agent流程"""
        # 这个方法也基本无需修改，我们之前已经修复了f-string的问题
        print(f"收到请求: {user_query}")

        print("\n[第一步: 规划...]")
        plan = self._planner(user_query)
        if not plan:
            print("  [规划失败] 未能生成有效的执行计划。")
            return
        print(f"  [规划完成] 生成计划:\n{json.dumps(plan, indent=2, ensure_ascii=False)}")

        print("\n[第二步: 执行...]")
        execution_results = self._executor(plan)
        print("  [执行完成] 所有工具调用结束。")
        print("  [执行结果]:")
        for tool, res in execution_results.items():
            indented_res = res.replace('\n', '\n      ')
            print(f"    - {tool}:\n      {indented_res}")

        print("\n[第三步: 合成报告...]")
        final_report = self._synthesizer(user_query, execution_results)
        print("  [合成完成]")

        print("\n" + "=" * 20 + " 最终报告 " + "=" * 20)
        print(final_report)
        print("=" * 52)