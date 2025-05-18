import logging

from project.const import Stage, Result


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

def get_post_prompt(base_prompt: str, context: dict, current_stage: Stage, current_result: Result) -> str:
    if current_stage == Stage.RACE:
        if current_result == Result.P1:
            prompt = f"{base_prompt}You just won the race (P1)! Write an ecstatic and thankful social media post. Mention your team, {context.get('team_name', 'Mach 5')}, and the thrill of victory. Include F1-style hashtags."
        elif current_result == Result.DNF:
            prompt = f"{base_prompt}You had a DNF (Did Not Finish) with your result being {str(current_result)}. Write a disappointed but resilient social media post. Express determination to bounce back. Include hashtags like #NeverGiveUp."
        elif current_result in [Result.P2, Result.P3, Result.TOP_3]:
            prompt = f"{base_prompt}You finished top 3 with your result being {str(current_result)}. Write a happy and encouraging social media post. Express determination to win next time. Include hashtags like #WeBack."
        elif current_result in [Result.P4, Result.P5, Result.TOP_5]:
            prompt = f"{base_prompt}You finished top 5 with your result being {str(current_result)}. Write somewhat happy social media post. Express determination to get better. Include hashtags like #F1."
        elif current_result in [getattr(Result, f"P{i}") for i in range(6, 21)]:
            prompt = f"{base_prompt}You finished a difficult race with your result being {str(current_result)}. Write a somewhat disappointed but resilient social media post. Express determination to bounce back. Include hashtags like #NeverGiveUp."
        else:
            prompt = f"{base_prompt}You are confused about what happened with the race, you did not place. Write a disappointed social media post. Express determination to bounce back. Include hashtags like #NeverGiveUp."
    elif current_stage in [Stage.FP1, Stage.FP2, Stage.FP3 ]:
        prompt = f"{base_prompt}You finished {str(current_result)} in {str(current_stage)}. You are not too excited or scared because it is just practice. Write a social media post showing you cannot wait for qualifying tomorrow, use F1 related hashtags"
    elif current_stage in [Stage.Q1, Stage.Q2, Stage.Q3]:
        prompt = f"{base_prompt}Write a focused social media post about the current qualifying session. You finished {str(current_result)} in {str(current_stage)} and want to prove something on tomorrow's race. Include F1 hashtags or emojis."
    else:
        prompt = f"{base_prompt}Write a general social media post about F1. Include hashtags."
    return prompt