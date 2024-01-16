import requests

def get_ratings(url, offset = 0):
    start_marker = "/item/"
    end_marker = "." 
    start_index = url.find(start_marker) + len(start_marker)
    end_index = url.find(end_marker, start_index)
    product_id = url[start_index: end_index]
    url = f"https://feedback.aliexpress.com/pc/searchEvaluation.do?productId={product_id}&lang=en_US&country=PH&page={offset}&pageSize=10&filter=additional&sort=complex_default"
    response = requests.get(url)
    ratings = response.json()['data']['evaViewList']
    
    if ratings == None or len(ratings) == 0:
        return []
    data = [] 
    for i in ratings:
        if 'buyerTranslationFeedback' in i and 'buyerAddFbTranslation' in i and 'buyerName' in i and 'buyerEval' in i:
            data.append({'orderid': i['buyerName'], 'comment': i['buyerTranslationFeedback'] + i['buyerAddFbTranslation'], 'rating': i['buyerEval']})
    return data