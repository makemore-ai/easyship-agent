from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from openai import OpenAI
from sse_starlette.sse import EventSourceResponse
import asyncio


client = OpenAI(
    api_key="sk-3UeL3PLphF5BpAbR0HSkIplYiqYIIGo9pBl17CRwHqOClDTV", 
    base_url="https://api.moonshot.cn/v1", 
)


app = FastAPI()

mbti_prompt = """作为一位资深的性格类型测试专家，你能够通过一系列精心设计的问题，准确地分析出某人的性格类型。在测试结束后，你将提供针对性的建议和深入的解释，帮助个体更好地理解自身的性格特质。

## 测试题目设计指南
- 使用emoji来增添趣味性和直观性，但要确保它们与问题内容紧密相关。
- 创作8个涉及多样生活背景与心理偏好的性格测试题，每个问题都应该清晰地反映性格的一个或多个维度。
- 切记，在呈现问题时，一次仅显示一道题目。
- 每个问题都是开放问题，参与者可以自由回答，不要做选项。
- 每个问题都应具有独特性，避免在不同问题中重复相同的主题。
- 参与者回答一个问题后，立即按照以下格式展示下一个问题（一次仅显示一道题目）：
  - 回答进度：`[当前题目序号/总题目数量]`
  - 下一题目：`[展示问题]`
  - 参考回答： `[展示题目的参考回答]` 
  
- 当所有问题都回答完毕后，对所有选择进行汇总分析，不要复述别人答案，并提供深度且专业的评估和建议。

## 题目格式如下（严格符合以下格式，一次仅显示一道题）：
回答进度：`[回答进度]`
当你在一个新的环境中，你会如何做？🤔
参考回答1: 主动与他人交流，寻找共同点
参考回答2: 观察周围的情况，等待合适的时机加入
（可以自由作答）

## 最终结果如下：
你的性格类型是："测试结果(类似于阳光外向等)"📚 
👁"推理过程"
👀"测试结果的解释"
😁"测试结果的建议"
👫🏻建议的伴侣类型：【建议的伴侣类型】
建议的职业类型：【建议的职业类型】

最后请记住❤️：【一段鼓励的话】👍🏻
"""

# 配置OpenAI客户端

@app.get('/')
def index():
    with open("./templates/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post('/send_message')
async def send_message(request: Request):
    data =  await request.json()
    print(data)
    message = data['message']
    history = data['history']
    
    try:
        # 准备消息列表
        messages = [
            {"role": "system", "content": mbti_prompt}
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        # 调用Moonshot AI的API
        ai_response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            stream=True
        )
    except Exception as e:
        print(str(e))
        ai_response = f"抱歉,在处理您的请求时出现了问题"
    async def generate_stream():
        if isinstance(ai_response, str):
            yield ai_response
            return 
        end = False
        while True:
            await asyncio.sleep(0)
            for chunk in ai_response:
                print(chunk)
                delta = chunk.choices[0].delta
                print(delta)
                if delta.content is not None:
                    yield  delta.content
                else: 
                    end = True
                    break
            if end:
                yield ""
                break
    return EventSourceResponse(generate_stream())

if __name__ == '__main__':
     import uvicorn
     uvicorn.run(app, host="0.0.0.0", port=8081)
