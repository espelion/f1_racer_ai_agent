import logging


LOGGER = logging.getLogger(__name__)
SENTIMENT_ANALYZER = None

try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import nltk
except ImportError:
    LOGGER.warning("NLTK not installed. Sentiment analysis in TemplateBasedTextGenerator will be basic. Run 'pip install nltk'")


if 'SentimentIntensityAnalyzer' in globals():
    try:
        # Download VADER lexicon if not already present
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        LOGGER.warning("VADER lexicon not found. Attempting to download for NLTK sentiment analysis.")
        nltk.download('vader_lexicon', quiet=True)
    SENTIMENT_ANALYZER = SentimentIntensityAnalyzer()
    LOGGER.info("VADER sentiment analyzer initialized for TemplateBasedTextGenerator.")

def sentiment_analysis(text: str) -> float:
    if SENTIMENT_ANALYZER is None:
        return None
    
    # Calculate the sentiment
    sentiment_scores = SENTIMENT_ANALYZER.polarity_scores(text)
    compound_score = sentiment_scores['compound']
    return compound_score

