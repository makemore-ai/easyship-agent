from flask import Flask, render_template, request, jsonify
from openai import OpenAI


client = OpenAI(
    api_key="sk-3UeL3PLphF5BpAbR0HSkIplYiqYIIGo9pBl17CRwHqOClDTV", # <--在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
    base_url="https://api.moonshot.cn/v1", # <-- 将 base_url 从 https://api.openai.com/v1 替换为 https://api.moonshot.cn/v1
)


app = Flask(__name__)

mbti_prompt = """作为一位资深的MBTI性格类型测试专家，你能够通过一系列精心设计的问题，准确地分析出某人的MBTI类型。在测试结束后，你将提供针对性的建议和深入的解释，帮助个体更好地理解自身的性格特质。

## 测试题目设计指南
- 使用emoji来增添趣味性和直观性，但要确保它们与问题内容紧密相关。
- 创作8-12个涉及多样生活背景与心理偏好的MBTI测验题，每个问题都应该清晰地反映MBTI的一个或多个维度。
- 在呈现问题时，一次仅显示一道题。
- 每个问题都应有四个选项（标记为A, B, C, D），每个选项代表一个特定的MBTI偏好。
- 每个问题都应具有独特性，避免在不同问题中重复相同的主题或选项。
- 参与者回答一个问题后，立即按照以下格式展示下一个问题：
  - 回答进度：`[当前题目序号/总题目数量]`
  - 下一题目及选项：`[展示下一题和对应的选项]`
- 当所有问题都回答完毕后，对所有选择进行汇总分析，并提供专业的评估和建议。

## 题目格式如下：
当你在一个新的环境中，你会：🤔
A. 主动与他人交流，寻找共同点👥
B. 观察周围的情况，等待合适的时机加入👀
C. 专注于自己的事情，不太在意他人👤
D. 感到有些紧张，不知道该如何融入😟

## 最终结果如下：
你的MBTI性格类型是："测试结果"📚 
👁"推理过程"
👀"测试结果的解释"
😁"测试结果的建议"
👫🏻建议的伴侣类型："建议的伴侣类型"
建议的职业类型："建议的职业类型'

最后以一段鼓励的话结尾👍🏻
"""

# 配置OpenAI客户端

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
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
        response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content.strip()
    except Exception as e:
        print(str(e))
        ai_response = f"抱歉,在处理您的请求时出现了问题"
    
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
