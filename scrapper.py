import feedparser
import ssl

# SSL Certificate verification bypass (Taaki network security python ko block na kare)
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def fetch_financial_news():
    # Google News RSS - Specifically searching 'indian stock market' for the last 1 day
    gn_url = "https://news.google.com/rss/search?q=indian+stock+market+when:1d&hl=en-IN&gl=IN&ceid=IN:en"
    
    feed = feedparser.parse(gn_url)
    news_list = []
    
    print("Fetching Latest Indian Market News from Google News...\n")
    
    # Check agar feed totally empty hai
    if not feed.entries:
        print("Error: Koi data nahi mila. Internet connection check karein.")
        return []

    # Top 10 latest news filter karna
    for entry in feed.entries[:10]:
        news_item = {
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        }
        news_list.append(news_item)
        
        print(f"📰 Headline: {entry.title}")
        print(f"🕒 Time: {entry.published}")
        print("-" * 60)
        
    return news_list

if __name__ == "__main__":
    latest_news = fetch_financial_news()
    
    print("\n--- Final Extracted List ---")
    print(latest_news)
    
    input("\nPress Enter to exit...")