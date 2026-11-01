import streamlit as st
import feedparser
import ssl
from transformers import pipeline

# Page Configuration (Browser Tab Title & Layout)
st.set_page_config(page_title="AI Market Trends", page_icon="📈", layout="wide")

# SSL Certificate bypass
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

SECTOR_LABELS = [
    "Banking and Finance", "IT and Software", "Automobile and EV", 
    "Energy, Oil and Gas", "FMCG and Retail", "Pharma and Healthcare", 
    "Infrastructure and Real Estate"
]

# --- CACHING AI MODELS ---
# Yeh decorator ensure karega ki 1GB+ ke models sirf ek baar load hon, har button click par nahi
@st.cache_resource(show_spinner="Loading Heavy AI Models in Background...")
def load_models():
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    sentiment = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    return classifier, sentiment

def fetch_financial_news():
    gn_url = "https://news.google.com/rss/search?q=indian+stock+market+when:1d&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(gn_url)
    if not feed.entries:
        return []
    
    return [{"title": entry.title, "link": entry.link, "published": entry.published} for entry in feed.entries[:15]]

def process_news_data(news_list, classifier, sentiment_pipeline):
    processed_data = []
    
    for news in news_list:
        news_text = news["title"]
        
        # 1. Sector Check
        classification = classifier(news_text, candidate_labels=SECTOR_LABELS)
        top_sector = classification['labels'][0]
        sector_confidence = classification['scores'][0] * 100
        
        if sector_confidence < 25:
            continue
            
        # 2. Sentiment Check
        result = sentiment_pipeline(news_text)[0]
        sentiment_label = result['label'].upper()
        sentiment_score = result['score'] * 100
        
        if sentiment_label == "NEUTRAL" or sentiment_score < 60:
            continue
            
        processed_data.append({
            "time": news["published"],
            "headline": news_text,
            "sector": top_sector,
            "sector_conf": round(sector_confidence, 1),
            "sentiment": "BULLISH 🟢" if sentiment_label == "POSITIVE" else "BEARISH 🔴",
            "sentiment_conf": round(sentiment_score, 1),
            "link": news["link"],
            "is_bullish": sentiment_label == "POSITIVE"
        })
        
    return processed_data

# --- STREAMLIT UI DESIGN ---

st.title("🏢 AI-Powered Indian Market Scanner")
st.markdown("This dashboard reads real-time news and uses AI to identify market sectors and determine whether their trends are bullish or bearish.")
st.divider()

# Load models silently in background
classifier_model, sentiment_model = load_models()

# The Magic Button
if st.button("🚀 Analyze Today's Market Trends", use_container_width=True, type="primary"):
    
    with st.spinner("AI is scraping and reading the latest news... Please wait!"):
        raw_news = fetch_financial_news()
        
        if not raw_news:
            st.error("⚠️ No news fetched today. Market might be closed or API is down.")
        else:
            final_signals = process_news_data(raw_news, classifier_model, sentiment_model)
            
            if not final_signals:
                st.warning("All news today seems Neutral. No strong Buy/Sell signals found.")
            else:
                st.success(f"Successfully processed! Found {len(final_signals)} strong actionable news items.")
                
                # Displaying Results in Creative Cards
                for item in final_signals:
                    # Color coding based on sentiment
                    card_color = "success" if item["is_bullish"] else "error"
                    
                    with st.container():
                        st.markdown(f"### {item['headline']}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="🎯 Target Sector", value=item["sector"], delta=f"AI Match: {item['sector_conf']}%")
                        with col2:
                            # Using Streamlit metrics for a clean look
                            st.metric(label="📈 Market Impact", value=item["sentiment"], delta=f"Confidence: {item['sentiment_conf']}%", delta_color="normal" if item["is_bullish"] else "inverse")
                        with col3:
                            st.caption(f"🕒 Published: {item['time']}")
                            st.markdown(f"[🔗 Read Full Article here]({item['link']})")
                        
                        st.divider()