import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

def clean_text_for_bert(text):

    text = text.lower()
    text = ' '.join(text.split("\n"))
    text = ' '.join(text.split(":"))
    text = ' '.join(text.split(";"))

    text = re.sub(r'http\S+|www\S+', ' ', text)

    text = text.translate(str.maketrans('', '', string.punctuation))

    tokens = word_tokenize(text)

    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    cleaned_text = ' '.join(tokens)

    return cleaned_text

if __name__ == '__main__':
    text = "Appearance:Cute\nQuality:Strong & Waterproof\nSuitability:Good\n\nI really recommend buying and the stickers are so cute I even used it to decorate my toploader with Nayeon on it!!! ❤️\n\nPlease buy from this shop I highly recommend buying and the stickers are so cute!"
    cleaned_text = clean_text_for_bert(text)
    print(cleaned_text)