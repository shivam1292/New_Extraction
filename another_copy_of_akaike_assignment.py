from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from googletrans import Translator
from gtts import gTTS
from collections import Counter

app = FastAPI()

class NewsRequest(BaseModel):
    company: str

# 🚀 **News Scraping Function**
def get_yahoo_news(company, max_articles=5):
    search_url = f'https://news.search.yahoo.com/search?p={company}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for item in soup.find_all('div', class_='NewsArticle', limit=max_articles):
        title_tag = item.find('h4')
        summary_tag = item.find('p')

        if title_tag and summary_tag:
            articles.append({
                'Title': title_tag.text.strip(),
                'Summary': summary_tag.text.strip(),
            })

    return articles

# ✅ **Sentiment Analysis**
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    return "Positive" if polarity > 0.05 else "Negative" if polarity < -0.05 else "Neutral"

# ✅ **Comparative Sentiment Analysis**
def comparative_sentiment_analysis(news_articles):
    sentiment_results = [analyze_sentiment(article["Summary"]) for article in news_articles]
    sentiment_counts = Counter(sentiment_results)

    return {
        "Sentiment Distribution": sentiment_counts,
        "Coverage Differences": [
            {
                "Comparison": "Some articles are positive while others discuss challenges.",
                "Impact": "Positive news boosts investor confidence, while negative news may cause concerns."
            }
        ]
    }

# ✅ **Translate to Hindi**
def translate_to_hindi(text):
    translator = Translator()
    return translator.translate(text, src="en", dest="hi").text

# ✅ **Text-to-Speech (TTS)**
def text_to_speech_hindi(text, filename="news_audio.mp3"):
    tts = gTTS(text=text, lang="hi")
    tts.save(filename)
    return filename

# 🚀 **API Endpoint**
@app.post("/analyze-news")
def analyze_news(request: NewsRequest):
    news_articles = get_yahoo_news(request.company)

    if not news_articles:
        return {"error": "No news found"}

    for article in news_articles:
        article["Sentiment"] = analyze_sentiment(article["Summary"])
        article["Hindi_Summary"] = translate_to_hindi(article["Summary"])

    comparative_results = comparative_sentiment_analysis(news_articles)

    # 🔊 Convert Hindi Text to Speech
    speech_text = " ".join([article["Hindi_Summary"] for article in news_articles])
    speech_file = text_to_speech_hindi(speech_text)

    return {
        "Company": request.company,
        "Articles": news_articles,
        "Comparative Sentiment Score": comparative_results,
        "Final Sentiment Analysis": "Overall, the news coverage is mixed.",
        "Audio": speech_file
    }
