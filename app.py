from flask import Flask, render_template, request, send_from_directory
import requests
from aliExpressAPI import searchAndGet
from analyticsPart import text_cleaner, bert_processing
import spacy
import plotly.graph_objects as go
import plotly
import json
import plotly.express as px
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

def highlight_keywords(review, keywords, keywordCount):
    highlighted_review = review
    for keyword in keywords:
        if keyword not in keywordCount:
            keywordCount[keyword] = highlighted_review.count(keyword)
        else:
            keywordCount[keyword] += highlighted_review.count(keyword)
        highlighted_review = highlighted_review.replace(keyword, f"<span style='background-color:green'>{keyword}</span>")
    return highlighted_review

def create_highlights(text, keywordCount):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    highlighted_text = highlight_keywords(text, keywords, keywordCount)
    return highlighted_text

@app.route('/')
def base():
    return render_template("base.html")

@app.route('/theteam')
def about():
    return render_template("theteam.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/search', methods=['POST', 'GET'])
def index():
    return render_template('search.html')

@app.route('/result', methods = ['POST'])
def result():
    try:
        url = request.form.get('query')
        nums = min(max(int(request.form.get('numReviews')),6),100)
        datas = [] 
        allPositiveWords = {}
        allNegativeWords = {}
        keywordCount = {}
        posnegneuCount = {'pos': 0, 'neu': 0, 'neg': 0 } 
        listX = []
        listY = [] 
        for i in range(0, int(nums/10) + 1 ):
            datas.extend(searchAndGet.get_ratings(url, i))
        htmlToDisplay = ''
        for i in datas: 
            htmlToDisplay += '<div class="item">'
            htmlToDisplay += 'buyer name: ' + i['orderid'] + '<br>'
            htmlToDisplay += 'Buyer Rating: ' + str(i['rating']) + '<br>'
            htmlToDisplay += 'Text: ' + create_highlights(i['comment'], keywordCount) + '<br>'
            i['cleaned_comment'] = text_cleaner.clean_text_for_bert(i['comment'])
            positivewords, negativewords, sentiment_label, sentiment_score = bert_processing.process_text(i['cleaned_comment'])
            
            for j in positivewords.keys():
                if j not in allPositiveWords:
                    allPositiveWords[j] = positivewords[j] 
                else:
                    allPositiveWords[j] += positivewords[j] 
            for j in negativewords.keys():
                if j not in allNegativeWords:
                    allNegativeWords[j] = negativewords[j] 
                else:
                    allNegativeWords[j] += negativewords[j] 
            htmlToDisplay += "Sentiment Score: "
            if sentiment_label == 'POS': 
                htmlToDisplay += f"<span style='background-color:blue'> +{sentiment_score}"
                posnegneuCount['pos'] += 1
                listX.append(i['rating']/25)
                listY.append(sentiment_score)
            elif sentiment_label == 'NEG':
                htmlToDisplay += f"<span style='background-color:red'> -{sentiment_score}"
                posnegneuCount['neg'] += 1
            else:
                htmlToDisplay += f"<span> {sentiment_score}"
                posnegneuCount['neu'] += 1
                listX.append(i['rating']/25)
                listY.append(-sentiment_score)
            htmlToDisplay += "</span><br>"
            htmlToDisplay += f"Positive Words: <span style='background-color:blue'>" + ' '.join(list(positivewords.keys())) + '</span><br>'
            htmlToDisplay += f"Negative Words: <span style='background-color:red'>" + ' '.join(list(negativewords.keys())) + '</span><br>'
            htmlToDisplay += '</div><br>'
        countSentiment = go.Figure(data=go.Pie(labels=list(posnegneuCount.keys()), values=list(posnegneuCount.values())))
        countSentiment.update_layout(
            title='Sentiment Count'
        )
        graphJSON = json.dumps(countSentiment, cls=plotly.utils.PlotlyJSONEncoder)
        line = px.scatter(x=listX, y=listY, trendline="ols")
        graphJSON2 = json.dumps(line, cls=plotly.utils.PlotlyJSONEncoder)
        frequentPositiveWords = go.Figure(data=go.Bar(y=list(allPositiveWords.keys()), x=list(allPositiveWords.values()), orientation='h'  ))
        frequentPositiveWords.update_layout(
            title='Positve Words Frequency'
        )
        graphJSON3 = json.dumps(frequentPositiveWords, cls=plotly.utils.PlotlyJSONEncoder)
        frequentNegativeWords = go.Figure(data=go.Bar(y=list(allNegativeWords.keys()), x=list(allNegativeWords.values()), orientation='h' ))
        frequentNegativeWords.update_layout(
            title='Negative Words Frequency'
        )
        graphJSON4 = json.dumps(frequentNegativeWords, cls=plotly.utils.PlotlyJSONEncoder)
        frequentKeyWords = go.Figure(data=go.Bar(y=list(keywordCount.keys()), x=list(keywordCount.values()), orientation='h' ))
        frequentKeyWords.update_layout(
            title='Keyword Frequency'
        )
        graphJSON5 = json.dumps(frequentKeyWords, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('result.html', htmlToPrint = htmlToDisplay, graphJSON = graphJSON, graphJSON2 = graphJSON2,
        graphJSON3 = graphJSON3, graphJSON4 = graphJSON4, graphJSON5 = graphJSON5)
    except Exception as e:
        print(e)
        return render_template('result.html', htmlToPrint = 'Something Went Wrong!')

if __name__ == '__main__':
    app.run(debug=True)