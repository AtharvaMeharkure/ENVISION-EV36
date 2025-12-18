# =====================================================================
# ENHANCED FAKE NEWS DETECTION SCRAPER WITH SELENIUM
# Supports 20+ News Websites | Advanced Analysis | Auto CSV Export
# =====================================================================

# -----------------------------
# INSTALL REQUIRED LIBRARIES
# -----------------------------
# Run these commands in terminal:
# pip install selenium pandas beautifulsoup4 lxml webdriver-manager
#hi
# -----------------------------
# IMPORT LIBRARIES
# -----------------------------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from urllib.parse import urlparse, urljoin
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys

# -----------------------------
# FAKE NEWS DETECTION SCRAPER
# -----------------------------
class EnhancedFakeNewsDetectionScraper:
    def __init__(self):
        self.data = []
        self.total_scraped = 0
        self.total_failed = 0

        # Known credible sources (expanded list)
        self.credible_sources = {
            'bbc.co.uk', 'bbc.com', 'reuters.com', 'apnews.com', 'npr.org',
            'theguardian.com', 'nytimes.com', 'wsj.com', 'washingtonpost.com',
            'cnn.com', 'abcnews.go.com', 'cbsnews.com', 'nbcnews.com', 'pbs.org',
            'bloomberg.com', 'economist.com', 'time.com', 'newsweek.com',
            'usatoday.com', 'latimes.com', 'chicagotribune.com', 'nypost.com',
            'foxnews.com', 'msnbc.com', 'politico.com', 'axios.com',
            'thehill.com', 'associated-press.com', 'aljazeera.com'
        }

        # Sensational/clickbait words (expanded)
        self.sensational_words = [
            'shocking', 'breaking', 'unbelievable', 'amazing', 'incredible',
            'you won\'t believe', 'urgent', 'warning', 'scandal', 'bombshell',
            'exposed', 'revealed', 'shocking truth', 'must see', 'viral',
            'outrageous', 'alarming', 'terrifying', 'miracle', 'secrets',
            'mind-blowing', 'devastating', 'explosive', 'unprecedented',
            'game-changer', 'jaw-dropping', 'stunning', 'crisis', 'emergency'
        ]

        # Bias words (expanded)
        self.bias_words = [
            'liberal', 'conservative', 'leftist', 'right-wing', 'fake news',
            'mainstream media', 'they don\'t want you to know', 'wake up', 'sheep',
            'liberal media', 'conservative media', 'radical', 'extreme',
            'propaganda', 'brainwashed', 'conspiracy', 'deep state'
        ]

    # -----------------------------
    # DOMAIN CREDIBILITY ANALYSIS
    # -----------------------------
    def extract_domain_credibility(self, url):
        """Analyze domain credibility and trustworthiness"""
        try:
            domain = urlparse(url).netloc.lower().replace('www.', '')
            is_credible = any(source in domain for source in self.credible_sources)
            
            # Suspicious TLDs
            suspicious_tlds = ['.xyz', '.top', '.click', '.link', '.gq', '.tk', 
                              '.ml', '.ga', '.cf', '.pw', '.cc']
            has_suspicious_tld = any(domain.endswith(tld) for tld in suspicious_tlds)
            
            # Suspicious patterns (typosquatting)
            suspicious_patterns = ['bbc.co-', 'cnn-news', 'reuters-', 'nytimes-']
            has_suspicious_pattern = any(pattern in domain for pattern in suspicious_patterns)
            
            # Calculate credibility score
            if is_credible:
                credibility_score = 1.0
            elif has_suspicious_tld or has_suspicious_pattern:
                credibility_score = 0.2
            else:
                credibility_score = 0.5

            return {
                'domain': domain,
                'is_credible_source': is_credible,
                'has_suspicious_tld': has_suspicious_tld,
                'has_suspicious_pattern': has_suspicious_pattern,
                'credibility_score': credibility_score
            }
        except Exception as e:
            return {
                'domain': 'unknown',
                'is_credible_source': False,
                'has_suspicious_tld': False,
                'has_suspicious_pattern': False,
                'credibility_score': 0.5
            }

    # -----------------------------
    # TITLE ANALYSIS
    # -----------------------------
    def analyze_title_features(self, title):
        """Analyze title for fake news indicators"""
        if not title or title == 'N/A':
            return {
                'title_length': 0, 'word_count': 0, 'sensational_count': 0,
                'bias_count': 0, 'has_excessive_caps': False, 'caps_word_count': 0,
                'exclamation_count': 0, 'question_count': 0, 'has_clickbait_pattern': False,
                'emotional_score': 0.0
            }
        
        title_lower = title.lower()
        words = title.split()
        
        # Count sensational and bias words
        sensational_count = sum(1 for word in self.sensational_words if word in title_lower)
        bias_count = sum(1 for word in self.bias_words if word in title_lower)
        
        # Check for excessive capitalization
        caps_words = [w for w in words if w.isupper() and len(w) > 2]
        has_excessive_caps = len(caps_words) > 2
        
        # Count punctuation
        exclamation_count = title.count('!')
        question_count = title.count('?')
        
        # Clickbait pattern detection
        clickbait_patterns = [
            r'you won\'t believe', r'what happened next', r'this one trick',
            r'doctors hate', r'number \d+ will', r'#\d+', r'wait until you see',
            r'the reason why', r'this is why', r'here\'s why', r'find out'
        ]
        has_clickbait = any(re.search(pattern, title_lower) for pattern in clickbait_patterns)
        
        # Calculate emotional score
        word_count = len(words)
        emotional_score = (sensational_count * 2 + bias_count + exclamation_count) / max(word_count, 1)

        return {
            'title_length': len(title),
            'word_count': word_count,
            'sensational_count': sensational_count,
            'bias_count': bias_count,
            'has_excessive_caps': has_excessive_caps,
            'caps_word_count': len(caps_words),
            'exclamation_count': exclamation_count,
            'question_count': question_count,
            'has_clickbait_pattern': has_clickbait,
            'emotional_score': round(emotional_score, 3)
        }

    # -----------------------------
    # CONTENT ANALYSIS
    # -----------------------------
    def analyze_content_features(self, description):
        """Analyze content for credibility indicators"""
        if not description or description == 'N/A':
            return {
                'content_length': 0, 'has_unattributed_claims': False,
                'has_citation': False, 'has_statistics': False
            }
        
        desc_lower = description.lower()
        
        # Check for unattributed claims
        has_unattributed_claims = bool(re.search(
            r'\b(i heard|they say|everyone knows|people are saying|it\'s obvious|rumor has it)\b',
            desc_lower
        ))
        
        # Check for citations/sources
        has_citation = bool(re.search(
            r'\b(according to|source|study|research|report|data shows|analysis|official|expert)\b',
            desc_lower
        ))
        
        # Check for statistics/numbers
        has_statistics = bool(re.search(
            r'\d+%|\d+\s*(million|billion|thousand|percent)',
            desc_lower
        ))

        return {
            'content_length': len(description),
            'has_unattributed_claims': has_unattributed_claims,
            'has_citation': has_citation,
            'has_statistics': has_statistics
        }

    # -----------------------------
    # RISK SCORE CALCULATION
    # -----------------------------
    def calculate_risk_score(self, domain_features, title_features, content_features):
        """Calculate overall fake news risk score (0-1)"""
        score = 0.0
        
        # Domain factors (40% weight)
        if not domain_features.get('is_credible_source'):
            score += 0.2
        if domain_features.get('has_suspicious_tld'):
            score += 0.15
        if domain_features.get('has_suspicious_pattern'):
            score += 0.05
        
        # Title factors (40% weight)
        if title_features.get('sensational_count', 0) > 1:
            score += 0.15
        if title_features.get('has_excessive_caps'):
            score += 0.1
        if title_features.get('exclamation_count', 0) > 2:
            score += 0.1
        if title_features.get('has_clickbait_pattern'):
            score += 0.05
        
        # Content factors (20% weight)
        if content_features.get('has_unattributed_claims'):
            score += 0.1
        if not content_features.get('has_citation'):
            score += 0.05
        if not content_features.get('has_statistics'):
            score += 0.05
        
        return round(min(score, 1.0), 3)

    # -----------------------------
    # SETUP SELENIUM DRIVER
    # -----------------------------
    def setup_driver(self):
        """Setup Chrome driver with optimized options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Suppress logs
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            driver.set_page_load_timeout(30)
            return driver
            
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            return None

    # -----------------------------
    # SCRAPE WITH SELENIUM
    # -----------------------------
    def scrape_with_analysis(self, url, source_name='Unknown'):
        """Scrape news website and analyze for fake news indicators"""
        print(f"\n{'='*70}")
        print(f"🌐 Scraping: {source_name}")
        print(f"📍 URL: {url}")
        print(f"{'='*70}")
        
        driver = None
        try:
            # Setup driver
            driver = self.setup_driver()
            if not driver:
                return False
            
            # Load page
            print("⏳ Loading page...")
            driver.get(url)
            time.sleep(5)  # Wait for dynamic content
            
            # Scroll to load more content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            # Domain credibility
            domain_features = self.extract_domain_credibility(url)
            
            # Find articles using multiple selectors
            articles = []
            selectors = [
                'article',
                'div.article',
                'div.story',
                'div.post',
                'div.news-item',
                'div[class*="article"]',
                'div[class*="story"]',
                'div[class*="item"]'
            ]
            
            for selector in selectors:
                found = soup.select(selector)
                if found and len(found) >= 3:
                    articles = found[:30]  # Get up to 30 articles
                    break
            
            if not articles:
                articles = soup.find_all(['article', 'div'], 
                                        class_=re.compile(r'(article|story|post|item)', re.I))[:30]
            
            print(f"📊 Found {len(articles)} articles")
            
            if not articles:
                print("⚠️  No articles found on this page")
                self.total_failed += 1
                return False
            
            # Extract and analyze each article
            extracted_count = 0
            for idx, article in enumerate(articles, 1):
                try:
                    # Extract title
                    title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    title = title_elem.get_text(strip=True) if title_elem else None
                    
                    if not title or len(title) < 10:
                        continue
                    
                    # Extract link
                    link_elem = article.find('a', href=True)
                    link = urljoin(url, link_elem['href']) if link_elem else 'N/A'
                    
                    # Extract description
                    desc_elem = article.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else 'N/A'
                    
                    # Extract date
                    date_elem = article.find(['time', 'span'], class_=re.compile(r'(date|time)', re.I))
                    pub_date = date_elem.get_text(strip=True) if date_elem else 'N/A'
                    
                    # Analyze features
                    title_features = self.analyze_title_features(title)
                    content_features = self.analyze_content_features(description)
                    risk_score = self.calculate_risk_score(domain_features, title_features, content_features)
                    
                    # Compile article data
                    article_data = {
                        'title': title,
                        'link': link,
                        'description': description[:500] if description != 'N/A' else 'N/A',
                        'pub_date': pub_date,
                        'source': source_name,
                        'source_url': url,
                        'extracted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        
                        # Domain features
                        'domain': domain_features['domain'],
                        'is_credible_source': domain_features['is_credible_source'],
                        'credibility_score': domain_features['credibility_score'],
                        
                        # Title features
                        'title_length': title_features['title_length'],
                        'sensational_count': title_features['sensational_count'],
                        'bias_count': title_features['bias_count'],
                        'has_excessive_caps': title_features['has_excessive_caps'],
                        'exclamation_count': title_features['exclamation_count'],
                        'has_clickbait_pattern': title_features['has_clickbait_pattern'],
                        'emotional_score': title_features['emotional_score'],
                        
                        # Content features
                        'content_length': content_features['content_length'],
                        'has_citation': content_features['has_citation'],
                        'has_statistics': content_features['has_statistics'],
                        'has_unattributed_claims': content_features['has_unattributed_claims'],
                        
                        # Risk assessment
                        'risk_score': risk_score
                    }
                    
                    self.data.append(article_data)
                    extracted_count += 1
                    
                    # Progress indicator
                    if extracted_count % 5 == 0:
                        print(f"  ✓ Extracted {extracted_count} articles...")
                    
                except Exception as e:
                    continue
            
            print(f"✅ Successfully extracted {extracted_count} articles from {source_name}")
            self.total_scraped += extracted_count
            return True
            
        except TimeoutException:
            print(f"⏰ Timeout loading {source_name}")
            self.total_failed += 1
            return False
            
        except Exception as e:
            print(f"❌ Error scraping {source_name}: {str(e)}")
            self.total_failed += 1
            return False
            
        finally:
            if driver:
                driver.quit()

    # -----------------------------
    # SAVE TO CSV
    # -----------------------------
    def save_to_csv(self, filename='fake_news_analysis.csv'):
        """Save extracted data to CSV file"""
        if not self.data:
            print("\n⚠️  No data to save!")
            return False
        
        try:
            df = pd.DataFrame(self.data)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"\n💾 Saved {len(df)} articles to '{filename}'")
            return True
        except Exception as e:
            print(f"\n❌ Error saving CSV: {str(e)}")
            return False

    # -----------------------------
    # GENERATE SUMMARY REPORT
    # -----------------------------
    def generate_summary_report(self):
        """Generate analysis summary"""
        if not self.data:
            print("\n⚠️  No data to analyze!")
            return
        
        df = pd.DataFrame(self.data)
        
        print("\n" + "="*70)
        print("📊 FAKE NEWS DETECTION SUMMARY REPORT")
        print("="*70)
        
        print(f"\n📈 EXTRACTION STATISTICS:")
        print(f"  Total Articles Analyzed: {len(df)}")
        print(f"  Sources Scraped: {df['source'].nunique()}")
        print(f"  Successful Scrapes: {self.total_scraped}")
        print(f"  Failed Scrapes: {self.total_failed}")
        
        print(f"\n🎯 RISK DISTRIBUTION:")
        high_risk = df[df['risk_score'] > 0.6]
        medium_risk = df[(df['risk_score'] > 0.3) & (df['risk_score'] <= 0.6)]
        low_risk = df[df['risk_score'] <= 0.3]
        
        print(f"  High Risk (>0.6):     {len(high_risk):4d} articles ({len(high_risk)/len(df)*100:5.1f}%)")
        print(f"  Medium Risk (0.3-0.6): {len(medium_risk):4d} articles ({len(medium_risk)/len(df)*100:5.1f}%)")
        print(f"  Low Risk (<0.3):      {len(low_risk):4d} articles ({len(low_risk)/len(df)*100:5.1f}%)")
        
        print(f"\n🏢 SOURCE ANALYSIS:")
        credible = df[df['is_credible_source'] == True]
        print(f"  Credible Sources: {len(credible)} articles ({len(credible)/len(df)*100:.1f}%)")
        
        print(f"\n📝 CONTENT INDICATORS:")
        print(f"  Sensational Language: {df[df['sensational_count'] > 0].shape[0]} articles")
        print(f"  Clickbait Patterns:   {df[df['has_clickbait_pattern'] == True].shape[0]} articles")
        print(f"  Has Citations:        {df[df['has_citation'] == True].shape[0]} articles")
        
        print(f"\n📊 AVERAGE SCORES:")
        print(f"  Risk Score:       {df['risk_score'].mean():.3f}")
        print(f"  Emotional Score:  {df['emotional_score'].mean():.3f}")
        print(f"  Credibility:      {df['credibility_score'].mean():.3f}")
        
        print(f"\n⚠️  TOP 5 MOST SUSPICIOUS ARTICLES:")
        top_suspicious = df.nlargest(5, 'risk_score')[['title', 'source', 'risk_score']]
        for idx, (_, row) in enumerate(top_suspicious.iterrows(), 1):
            print(f"  {idx}. [{row['risk_score']:.3f}] {row['source']}")
            print(f"     {row['title'][:80]}...")
        
        print("\n" + "="*70)


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def main():
    """Main execution function"""
    print("="*70)
    print("🚀 ENHANCED FAKE NEWS DETECTION SCRAPER")
    print("="*70)
    print("Features:")
    print("  ✓ 20+ Major News Sources")
    print("  ✓ Advanced Credibility Analysis")
    print("  ✓ Fake News Risk Scoring")
    print("  ✓ Automatic CSV Export")
    print("="*70)
    
    # Initialize scraper
    scraper = EnhancedFakeNewsDetectionScraper()
    
    # Comprehensive list of news websites to scrape
    urls_to_scrape = [
        # Major US News
        ('https://www.cnn.com/', 'CNN'),
        ('https://www.bbc.com/news', 'BBC News'),
        ('https://www.reuters.com/', 'Reuters'),
        ('https://apnews.com/', 'AP News'),
        ('https://www.nytimes.com/', 'New York Times'),
        ('https://www.washingtonpost.com/', 'Washington Post'),
        ('https://www.theguardian.com/us', 'The Guardian'),
        ('https://www.usatoday.com/', 'USA Today'),
        ('https://www.nbcnews.com/', 'NBC News'),
        ('https://abcnews.go.com/', 'ABC News'),
        ('https://www.cbsnews.com/', 'CBS News'),
        ('https://www.foxnews.com/', 'Fox News'),
        
        # Business & Finance
        ('https://www.bloomberg.com/', 'Bloomberg'),
        ('https://www.wsj.com/', 'Wall Street Journal'),
        ('https://www.cnbc.com/', 'CNBC'),
        
        # Technology
        ('https://www.theverge.com/', 'The Verge'),
        ('https://techcrunch.com/', 'TechCrunch'),
        ('https://www.wired.com/', 'Wired'),
        
        # International
        ('https://www.aljazeera.com/', 'Al Jazeera'),
        ('https://www.dw.com/en/', 'Deutsche Welle'),
        
        # Political
        ('https://www.politico.com/', 'Politico'),
        ('https://thehill.com/', 'The Hill'),
        ('https://www.axios.com/', 'Axios'),
        
        # Additional Sources
        ('https://www.npr.org/', 'NPR'),
        ('https://time.com/', 'TIME'),
    ]
    
    print(f"\n🎯 Will scrape {len(urls_to_scrape)} news sources")
    input("\nPress Enter to start scraping...")
    
    start_time = time.time()
    
    # Scrape each website
    for idx, (url, source) in enumerate(urls_to_scrape, 1):
        print(f"\n[{idx}/{len(urls_to_scrape)}]")
        scraper.scrape_with_analysis(url, source)
        time.sleep(3)  # Be polite between requests
    
    # Calculate execution time
    elapsed_time = time.time() - start_time
    
    # Save results
    print("\n" + "="*70)
    print("💾 SAVING RESULTS")
    print("="*70)
    scraper.save_to_csv('fake_news_analysis.csv')
    
    # Generate report
    scraper.generate_summary_report()
    
    # Final summary
    print("\n" + "="*70)
    print("✅ SCRAPING COMPLETE!")
    print("="*70)
    print(f"⏱️  Total Time: {elapsed_time/60:.1f} minutes")
    print(f"📊 Total Articles: {len(scraper.data)}")
    print(f"📄 Output File: fake_news_analysis.csv")
    print("\n💡 Next Steps:")
    print("  1. Open 'fake_news_analysis.csv' in Excel or Python")
    print("  2. Analyze the risk scores and credibility features")
    print("  3. Use the data for ML model training")
    print("  4. Filter high-risk articles for further investigation")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        sys.exit(1)