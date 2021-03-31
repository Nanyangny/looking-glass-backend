from flask import Flask , jsonify, request
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["DEBUG"] = True


# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/books',methods=['GET'])
def api_id():
    if 'id' in request.args:
        id = int(request.args['id'])
        res = requests.get("https://theconversation.com/eksploitasi-pekerja-magang-di-start-up-bisa-terjadi-karena-aturan-hukum-yang-ketinggalan-zaman-157353").text
        print(res)
        
    else:
        return "Error: No id field provided. Please specify an id."

    results = []
    for book in books:
        if book['id']==id:
            results.append(book)
    return jsonify(results)

@app.route('/news',methods=['GET'])
def api_news():
    results ={}
    if 'url' in request.args:
        url = request.args['url']
        news_domain = re.search('https://\w+.com/',url)[0]
        res = requests.get(url).text
        soup = BeautifulSoup(res, 'html.parser')
        basic_info = get_og_info(soup)
        ## for Conversation
        authors = get_author_info(soup,news_domain)
        past_convs = get_past_conv(soup)
        published_time = soup.select("#article > figure > div.magazine-title > div > header > time")[0]['datetime']
        results['past_conv']=past_convs
        results['og'] = basic_info
        results['authors']= authors
        results['pub_time']=published_time

    if 'keyword' in request.args:
        ### keyword search
        
        keyword= request.args['keyword']
        # search_key = "+".join(keyword.strip().split(" "))
        # res = requests.get("https://www.youtube.com/results?search_query={}".format(search_key))
        results['topic'] = keyword
        response = jsonify(results)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
        
    else:
        return "Error: No id field provided. Please specify an id."

    results = []
    for book in books:
        if book['id']==id:
            results.append(book)
    return jsonify(results)


def get_og_info(soup_input):
    meta = soup_input.find_all('meta')
    og ={}
    for item in meta:
        if "property" in item.attrs.keys():
            if item['property'].startswith("og:"):
                og[item['property'].split('og:')[1]]=item['content']
        
    return og

def get_author_info(soup_input,domain):
    authors = []
    authors_list = soup_input.find_all('div','content-authors-group')[0].find_all('li')
    for item in authors_list:
        aut_url= domain+item.find_all('a')[0]['href']
        aut_img_url= item.find_all('img')[0]['src']
        aut_name=item.find_all('span')[0].text.strip()
        aut_title= item.find_all('p','role')[0].text.strip()
        author = {'author_url':aut_url,'url':aut_img_url,'name':aut_name,'role':aut_title}
        authors.append(author)

    return authors

def get_past_conv(soup_input):
    past_conv = soup_input.select("p em strong")
    past_convs=[]
    for conv in past_conv:
        conv = conv.find_all('a')[0]
        conv_headline = conv.text
        conv_url = conv['href']
        conv_dic = {
            "headline":conv_headline,
            "url":conv_url
        }
        past_convs.append(conv_dic)
    return past_convs

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)