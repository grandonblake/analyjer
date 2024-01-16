from transformers import pipeline
from transformers import AutoTokenizer
import torch 
device = "cuda:0" if torch.cuda.is_available() else "cpu"
sentiment_classifier = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def process_text(text):
    tokens = tokenizer.tokenize(text)
    result = sentiment_classifier(text)[0]
    sentiment_label = result['label']
    sentiment_score = result['score']
    positivewords = {}
    negativewords = {}
    for token in tokens:
        token_sentiment = sentiment_classifier(token)[0]
        token_score = token_sentiment['score']
        if token_score >= 0.6 and token_sentiment['label'] == 'POS':
            if token not in positivewords:
                positivewords[token] = 1 
            else:
                positivewords[token] += 1 
        elif token_score >= 0.6 and token_sentiment['label'] == 'NEG':
            if token not in negativewords:
                negativewords[token] = 1 
            else:
                negativewords[token] += 1 
    return positivewords, negativewords, sentiment_label, sentiment_score
