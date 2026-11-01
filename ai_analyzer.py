import feedparser
import ssl
from transformers import pipeline

# SSL Certificate bypass
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Sectors ki list (AI inme se best sector choose karega)
SECTOR_LABELS = [
    "Banking and Finance",
    "IT and Software",
    "Automobile and EV",
    "Energy, Oil and Gas",
    "FMCG and Retail",
    "Pharma and Healthcare",
    "Infrastructure and Real Estate"
]

def fetch_financial_news():
    # Google News se market news fetch karna
    gn_url = "https://news.google.com/rss/search?q=indian+stock+market+when:1d&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(gn_url)
    
    if not feed.entries:
        return []
    
    news_items = []
    # Fetching Top 15 news articles with Title, Link, and Timestamp
    for entry in feed.entries[:15]:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })
    return news_items

def analyze_sector_trends():
    news_list = fetch_financial_news()
    
    if not news_list:
        print("⚠️ No news fetched today. Market might be closed or no breaking news available.")
        return

    print("Loading AI Models (Classifier & Sentiment)... Please wait.\n")
    
    # AI Models load karna
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    
    print("="*100)
    print("🏢 AI SECTOR TRENDS & NEWS SENTIMENT 🏢")
    print("="*100)
    
    for news in news_list:
        news_text = news["title"]
        news_link = news["link"]
        news_time = news["published"]
        
        # 1. Sector Classification
        classification = classifier(news_text, candidate_labels=SECTOR_LABELS)
        top_sector = classification['labels'][0]
        sector_confidence = classification['scores'][0] * 100
        
        # Sector match confidence thoda kam ho toh skip karein
        if sector_confidence < 25:
            continue
            
        # 2. Sentiment Analysis
        result = sentiment_pipeline(news_text)[0]
        sentiment_label = result['label'].upper()
        sentiment_score = result['score'] * 100
        
        # Sirf strong signals dekhne ke liye Neutral ya low confidence news ignore kar rahe hain
        if sentiment_label == "NEUTRAL" or sentiment_score < 60:
            continue
            
        trend = "🟢 BULLISH" if sentiment_label == "POSITIVE" else "🔴 BEARISH"
        
        # 3. Final Output (With Timestamp and Link)
        print(f"🕒 Time   : {news_time}")
        print(f"📰 News   : {news_text}")
        print(f"🎯 Sector : {top_sector} (AI Match: {sector_confidence:.1f}%)")
        print(f"📈 Impact : {trend} (Confidence: {sentiment_score:.1f}%)")
        print(f"🔗 Link   : {news_link}")
        print("-" * 100)

if __name__ == "__main__":
    analyze_sector_trends()