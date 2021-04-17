from flask import Flask , jsonify, request
import requests
import re
from bs4 import BeautifulSoup
import urllib


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


# @app.route('/books',methods=['GET'])
# def api_id():
#     if 'id' in request.args:
#         id = int(request.args['id'])
#         res = requests.get("https://theconversation.com/eksploitasi-pekerja-magang-di-start-up-bisa-terjadi-karena-aturan-hukum-yang-ketinggalan-zaman-157353").text
#         print(res)
        
#     else:
#         return "Error: No id field provided. Please specify an id."

#     results = []
#     for book in books:
#         if book['id']==id:
#             results.append(book)
#     return jsonify(results)

@app.route('/news',methods=['GET'])
def api_news():
    result ={}
    if 'url' in request.args:
        url = request.args['url']
        if url.startswith('https://theconversation.com/'):
            news_domain = re.search('https://\w+.com/',url)[0]
            res = requests.get(url).text
            soup = BeautifulSoup(res, 'html.parser')
            basic_info = get_og_info(soup)
            ## for Conversation
            authors = get_author_info(soup,news_domain)
            past_convs = get_past_conv(soup)
            try:
                published_time = soup.select("#article > figure > div.magazine-title > div > header > time")[0]['datetime']
            except:
                published_time = soup.select("#article > div:nth-child(1) > div > header > time")[0]['datetime']
            result['past_conv']=past_convs
            result['og'] = basic_info
            result['authors']= authors
            result['pub_time']=published_time

        else:
            res = urllib.request.urlopen(url).read().decode("utf8")
            soup = BeautifulSoup(res, 'html.parser')
            basic_info = get_og_info(soup)
            result['og'] = basic_info
            result['pub_time'] = get_pub_time(soup)

    if 'keyword' in request.args:
        ### keyword search
        keyword= request.args['keyword']
        # search_key = "+".join(keyword.strip().split(" "))
        # res = requests.get("https://www.youtube.com/results?search_query={}".format(search_key))
        result['topic'] = keyword
        response = jsonify(result)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
        
    else:
        return "Error: No id field provided. Please specify an id."


## for topic quick review
@app.route('/basics',methods=['GET'])
def api_basics():
    result ={}
    if 'url' in request.args:
        url = request.args['url']
        res = requests.get(url).text
        soup = BeautifulSoup(res, 'html.parser')
        basic_info = get_og_info(soup)
        result['og'] = basic_info
        result['pub_time'] = get_pub_time(soup)
        response = jsonify(result)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        return "Error: No id field provided. Please specify an id."






@app.route('/videos',methods=['GET'])
def api_youtube():
    if 'keyword' in request.args:
        keyword = request.args['keyword']
        response = jsonify(get_youtube_video(keyword))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

@app.route('/global',methods=['GET'])
def api_global():
    if 'keyword' in request.args:
        keyword = request.args['keyword']
        response = jsonify(get_global_coverage(keyword))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response



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
        aut_img_url= item.find_all('img')[0]['data-src']
        aut_name=item.find_all('span')[0].text.strip()
        aut_title= item.find_all('p','role')[0].text.strip()
        author = {'author_url':aut_url,'url':aut_img_url,'name':aut_name,'role':aut_title}
        authors.append(author)

    return authors



def get_pub_time(soup_input):
    for item in soup_input.find_all('time'):
        if item['datetime']:
            return item['datetime']
    return ""


def get_past_conv(soup_input):
    past_conv = soup_input.select("p em strong")
    past_convs=[]
    for conv in past_conv:
        conv = conv.find_all('a')[0]
        conv_headline = conv.text
        conv_url = conv['href']

        # news_domain = re.search('https://\w+.com/',url)[0]
        res = requests.get(conv_url).text
        soup = BeautifulSoup(res, 'html.parser')
        meta = soup.find_all('meta')
        for item in meta:
            if "property" in item.attrs.keys():
                if item['property'].startswith("og:description"):
                    conv_desc = item['content']
                    break
        conv_dic = {
            "headline":conv_headline,
            "url":conv_url,
            "summary": conv_desc,
        }
        past_convs.append(conv_dic)
    return past_convs


def get_youtube_video(keyword):
    keyword_encoded = urllib.parse.quote(keyword)
    youtubes = []
    for i in range(0,50,10):
        if len(youtubes)<3:
            google_videosearh = requests.get("https://www.google.com/search?q={}&source=lnms&tbm=vid&start={}".format(keyword_encoded,i)).text
        # print(google_videosearh)
            soup = BeautifulSoup(google_videosearh, 'html.parser')

            a_tags = soup.find_all('a')
            for item in a_tags:
                youtube = {}
                if item['href'].startswith("/url?q=https://www.youtube.com/"):
                    try: 
                        extracted_vid_url = re.search(r'(https://\w+.\w+.com/watch[%\w]+)',item['href'])[0]
                        decoded_url = urllib.parse.unquote(extracted_vid_url)
                        decoded_url = "https://www.youtube.com/embed/"+decoded_url.split('https://www.youtube.com/watch?v=')[1]
                        youtube['url']=decoded_url
                        youtube['desc']=item.find_all('h3')[0].text.split(' | ')[0]
                        youtubes.append(youtube)
                        if len(youtubes)==3:
                            return youtubes
                    except:
                        pass
        else:
            break


def get_global_coverage(keyword,count=5):
    keyword_encoded = urllib.parse.quote(keyword)
    google_videosearh = requests.get("https://www.google.com/search?q={}&source=lnms&tbm=nws&start={}".format(keyword_encoded,0)).text
    orig_soup = BeautifulSoup(google_videosearh, 'html.parser').prettify()
    soup= BeautifulSoup(orig_soup, 'html.parser')
    global_news=[]
    for item in soup.find_all('a'):
        try:
            if item.attrs['href'].startswith("/url?q=https://"):
                text = item.attrs['href']
                if 'google' not in text:
                    global_news.append(text.split('/url?q=')[1].split('&')[0])        
        except:
            pass
        
    prev = ''
    filtered_glob_news=[]
    ## searching four info
    og_list = ["og:site_name","og:image","og:url","og:title"]
    glob_news_limit = count
    for i in range(0,len(global_news),2):
        if len(filtered_glob_news)<glob_news_limit:
            try:
                news_url = global_news[i]
                curr = re.search('https://([\w+]+.[\w+]+.[\w+]+/)',news_url)[0]
                if not curr ==prev: 
                    prev=curr
                    glob_output ={}
                    page_test = requests.get(news_url).text
                    soup= BeautifulSoup(page_test, 'html.parser')
                    for item in soup.find_all('meta'):
                        if len(glob_output.keys())<4:
                            try:
                                if item.attrs['property'] in og_list:
                                    glob_output[item.attrs['property']]=item.attrs['content']
                            except:
                                pass
                        else:
                            break
                    res_found = soup.find_all('link')[:30]
                    for item in res_found:
                        icon_result = item['rel'][0].find('icon')>=0
                        if icon_result:
                            icon_url = item['href']
        #                     print(icon_url)
                            if not icon_url.startswith("https:"):
                                glob_output['icon_url']= curr[:-1] + icon_url
                            else:
                                glob_output['icon_url']=icon_url
                    if len(glob_output.keys())==5 or glob_output.keys()==og_list:
                        filtered_glob_news.append(glob_output)
            except:
                continue
        else:
            break

    return filtered_glob_news
    
        


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)