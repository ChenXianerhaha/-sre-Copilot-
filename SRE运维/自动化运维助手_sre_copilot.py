# SRE Copilot Pro: 项目级 AI 运维 Agent（含 Web 界面 + LLM）

# ========================
# 安装依赖：
# pip install fastapi uvicorn openai
# ========================

import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# 如果你有 OpenAI API Key，取消下面注释
# from openai import OpenAI
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="SRE Copilot Pro")

# ====== 数据模型 ======
class InputData(BaseModel):
    logs: List[str]
    metrics: List[int]

# ====== Agents ======
class LogAnalyzerAgent:
    def run(self, logs):
        return [l for l in logs if "ERROR" in l or "Exception" in l]

class AnomalyAgent:
    def run(self, metrics):
        avg = sum(metrics)/len(metrics)
        return [m for m in metrics if m > avg * 1.5]

class LLMAgent:
    def run(self, errors, anomalies):
        prompt = f"""
你是一个SRE专家，请根据以下信息分析系统故障根因并给出修复建议：

错误日志：{errors}
异常指标：{anomalies}

输出：
1. 根因
2. 修复建议
"""

        # ====== 如果有 API Key，用真实 LLM ======
        # response = client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return response.choices[0].message.content

        # ====== 没 Key fallback ======
        if errors and anomalies:
            return "可能为高负载导致数据库连接耗尽，建议扩容+优化SQL"
        return "暂无明显问题"

# ====== Orchestrator ======
@app.post("/analyze")
def analyze(data: InputData):
    log_agent = LogAnalyzerAgent()
    anomaly_agent = AnomalyAgent()
    llm_agent = LLMAgent()

    errors = log_agent.run(data.logs)
    anomalies = anomaly_agent.run(data.metrics)
    result = llm_agent.run(errors, anomalies)

    return {
        "errors": errors,
        "anomalies": anomalies,
        "analysis": result
    }

# ====== 首页（简单 UI） ======
@app.get("/")
def home():
    return {
        "message": "SRE Copilot Pro is running",
        "usage": "POST /analyze"
    }

# ========================

