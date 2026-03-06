import os
import requests
import feedparser
from openai import OpenAI
from datetime import datetime

# 获取你的两把钥匙
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
AI_API_KEY = os.environ.get("AI_API_KEY")

# 连接硅基流动大模型（完全兼容 OpenAI 格式）
client = OpenAI(
    api_key=AI_API_KEY,
    base_url="https://api.siliconflow.cn/v1"
)

def get_news():
    """去新浪新闻抓取今日焦点新闻"""
    url = "https://rss.sina.com.cn/news/china/focus15.xml"
    feed = feedparser.parse(url)
    news_list = []
    for entry in feed.entries[:8]: # 抓取前8条
        news_list.append(entry.title)
    return "\n".join(news_list)

def analyze_news(news_text):
    """让 AI 算命并写报告"""
    prompt = f"你是我的私人情报分析师。请阅读以下今日新闻，总结核心内容，并预测这些事件可能对金融、生活或教育科研产生的潜在影响：\n{news_text}"
    
    # 使用阿里开源的通义千问模型（在硅基流动上永久免费！）
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_wechat(content):
    """把报告发给微信"""
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": f"💡 今日AI新闻预测 {datetime.now().strftime('%Y-%m-%d')}",
        "content": content
    }
    requests.post(url, json=data)

def update_webpage(content):
    """把报告做成一个漂亮的网页"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>每日情报预测</title></head>
    <body style="font-family: sans-serif; padding: 20px; max-width: 800px; margin: auto; background-color: #f4f4f9;">
        <h1 style="color: #333; text-align: center;">🌍 今日新闻与AI深度预测</h1>
        <p style="text-align: center; color: #888;">更新时间：{datetime.now().strftime('%Y-%m-%d')}</p>
        <div style="background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); white-space: pre-wrap; line-height: 1.8; font-size: 16px; color: #444;">{content}</div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    print("1. 正在抓取新闻...")
    news = get_news()
    print("2. 正在呼叫 AI 大脑进行分析...")
    analysis = analyze_news(news)
    print("3. 正在发送微信提醒...")
    send_wechat(analysis)
    print("4. 正在生成今日网页...")
    update_webpage(analysis)
    print("🎉 全部任务搞定！")
