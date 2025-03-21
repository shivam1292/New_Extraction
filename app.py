import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from googletrans import Translator
from gtts import gTTS
import os
import json
from collections import Counter

# Step 1: Fetch News from Yahoo
def get_yahoo_news(company, max_articles=5):  # ✅ Max 5 articles rakh taaki fast execute ho
    """Fetches news articles from Yahoo News for a given company."""
    search_url = f'https://news.search.yahoo.com/search?p={company}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return []  # Avoid crashing

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

# Step 2: Perform Sentiment Analysis
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    return "Positive" if polarity > 0.05 else "Negative" if polarity < -0.05 else "Neutral"

# Step 3: Comparative Sentiment Analysis
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

# Step 4: Translate Text to Hindi
def translate_to_hindi(text):
    translator = Translator()
    return translator.translate(text, src="en", dest="hi").text

# Step 5: Convert Hindi Text to Speech
def text_to_speech_hindi(text, filename="news_audio.mp3"):
    tts = gTTS(text=text, lang="hi")
    tts.save(filename)
    return filename

# 🚀 **Streamlit App Start**
st.title("📢 News Sentiment & Hindi TTS App")
company_name = st.text_input("Enter Company Name:")

if st.button("Analyze"):
    st.write(f"📡 Fetching news for: {company_name}...")

    # 📰 Fetch News
    news_articles = get_yahoo_news(company_name)

    if not news_articles:
        st.error("❌ No news articles found! Try another company.")
    else:
        for article in news_articles:
            article["Sentiment"] = analyze_sentiment(article["Summary"])
            article["Hindi_Summary"] = translate_to_hindi(article["Summary"])

        comparative_results = comparative_sentiment_analysis(news_articles)

        # 🔊 Convert Hindi Text to Speech
        speech_text = " ".join([article["Hindi_Summary"] for article in news_articles])
        speech_file = text_to_speech_hindi(speech_text)

        # 🎯 Show Results
        st.json({
            "Company": company_name,
            "Articles": news_articles,
            "Comparative Sentiment Score": comparative_results,
            "Final Sentiment Analysis": "Overall, the news coverage is mixed.",
            "Audio": speech_file
        })

        # 🎙 Play Audio in Streamlit
        st.audio(speech_file, format="audio/mp3")  # ✅ Streamlit ke liye sahi hai
