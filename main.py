import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import feedparser
from openai import OpenAI
from datetime import datetime

# 获取你的秘钥和邮箱信息
QQ_EMAIL = os.environ.get("QQ_EMAIL")
QQ_AUTH_CODE = os.environ.get("QQ_AUTH_CODE")
AI_API_KEY = os.environ.get("AI_API_KEY")

# 连接硅基流动大模型
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
    
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_email(content):
    """把报告发送到 QQ 邮箱"""
    smtp_server = "smtp.qq.com"
    smtp_port = 465 # QQ邮箱的加密端口
    
    # 准备邮件内容
    msg = MIMEMultipart()
    msg['From'] = QQ_EMAIL
    msg['To'] = QQ_EMAIL  # 发件人和收件人都是你自己
    msg['Subject'] = f"💡 今日AI新闻预测 {datetime.now().strftime('%Y-%m-%d')}"
    
    # 把内容放进邮件正文
    body = MIMEText(content, 'plain', 'utf-8')
    msg.attach(body)
    
    # 发送动作
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(QQ_EMAIL, QQ_AUTH_CODE)
        server.sendmail(QQ_EMAIL, [QQ_EMAIL], msg.as_string())
        server.quit()
        print("✅ QQ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

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
    print("3. 正在发送QQ邮件提醒...")
    send_email(analysis)
    print("4. 正在生成今日网页...")
    update_webpage(analysis)
    print("🎉 全部任务搞定！")
