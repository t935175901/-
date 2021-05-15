# -*- coding: utf-8 -*-

import math
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from xlrd import open_workbook
from config import *
import tqdm
from math import e
from retry import retry
from fake_useragent import UserAgent

import requests
from bs4 import BeautifulSoup as BS
datas = []
#无效
def verification(url):
    driver = webdriver.Chrome()
    driver.get(url)
    print('请手动验证')
    os.system("pause")
    # try:
    #     path=driver.find_elements_by_xpath('//div[@class="rc-anchor-center-container"]')[0]
    #     path.click()
    # except:
    #     print("something wrong")
def lemmatize_all(tagged):#词性还原
    temp=[]
    wnl = WordNetLemmatizer()
    for n in tagged:
        if n[1].startswith('NN') and not n[1].startswith('NNP'):
            temp.append((wnl.lemmatize(n[0], pos='n'),'NN'))
        elif n[1].startswith('VB'):
            temp.append((wnl.lemmatize(n[0], pos='v'),'VB'))
        elif n[1].startswith('JJ'):
            temp.append((wnl.lemmatize(n[0], pos='a'),'JJ'))
        elif n[1].startswith('RB'):
            temp.append((wnl.lemmatize(n[0], pos='r'),"RB"))
        else:
            temp.append(n)
    return temp
#随机头
def get_header():
    location = os.getcwd() + '/agent.json'
    ua = UserAgent(path=location)
    return ua.random

#通过谷歌获取该新闻在其新闻网站的网址
#!!!即使手动通过也无用
#@retry( tries=3, delay=2)
def search(term, proxies,num_results=10, lang="en"):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.100 Safari/537.36'}
    def fetch_results(search_term, number_results, language_code):
        escaped_search_term = search_term.replace(' ', '+')

        google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results+1,
                                                                              language_code)
        response = requests.get(google_url, headers=usr_agent,proxies=proxies)
        response.raise_for_status()
        return response.text

    def parse_results(raw_html):
        soup = BS(raw_html, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block:
            link = result.find('a', href=True)
            title = result.find('h3')
            if link and title:
                yield link['href']

    html = fetch_results(term, num_results, lang)
    return list(parse_results(html))

def get_url(data,nn):
    #headers = {'User-Agent': get_header()}
    proxy = {"https": "socks5h://127.0.0.1:10808"}
    for source in sources[nn]:
        text = data['text'] + ' site:' + source['url']
        if x:=search(text,proxies=proxy):
            return no_from_twitter(x)
    text = data['text']
    if x := search(text, proxies=proxy):
        return no_from_twitter(x)

    #无法连接尝试换掉，
    #url='https://www.google.com/search'
    #session = HTMLSession()
    #params = {'q': data['text'] + ' site:' + india_sources[data['from']]['url']}

    #r = session.get(url=url, params=params, proxies=proxy, timeout=4, headers=headers)
    # if r.status_code==429:
    #     verification(r.url)
    #     #暂停手动验证
    #     raise Exception
    # if x := r.html.xpath('//*[@id="rso"]/div[1]/div//div[1]/a'):
    #     return x[0].attrs['herf']
    # 有时候site太严格无结果用link凑合
    # else:
    #     params = {'q': data['text'] + ' link:' + india_sources[data['from']]['url']}
    #     r = session.get(url=url, params=params, proxies=proxy, timeout=4, headers=headers)
    #     if r.status_code==429:
    #         verification(r.url)
    #         #暂停手动验证
    #         raise Exception
    #     return r.html.xpath('//*[@id="rso"]/div[1]/div//div[1]/a')[0].attrs["href"]

#去掉来自本站的网址
def no_from_twitter(url_list):
    for url in url_list:
        if 'twitter.com/' not in url:
           return url
#关键词提取
def extract(text):
    # 读取文件
    tokens = nltk.word_tokenize(text)
    # 去掉标点符号和停用词
    # 去掉标点符号
    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
    text_list = [word for word in tokens if word not in english_punctuations]
    # 去掉停用词
    stops = set(stopwords.words("english"))
    tokens = [word for word in text_list if word not in stops]
    # 分词
    tagged = nltk.pos_tag(tokens)  # 词性标注
    tagged = lemmatize_all(tagged)
    #tags = ('CD', 'FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS', 'RBR', 'RBS', 'RP', 'VB', 'VBD', 'VBG', 'VBN', 'VBP','VBZWRB')#词性过滤
    tags = ( 'CD','FW', 'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP','VBZWRB')
    #仅提取如下词性作为关键词
    #数字，外来词，形容词，名词，专有名词，动词
    ret = []
    for word, pos in tagged:
        if pos in tags:
            ret.append(word)
    # entities = nltk.chunk.ne_chunk(tagged)  #命名实体识别
    # a1=str(entities) #将文件转换为字符串
    # file_object = open('output.txt', 'w')
    # file_object.write(a1)   #写入到文件中
    # file_object.close( )
    # print (entities)
    return ret
#简单的余弦相似度比较
def similary(str1,str2):
    word_dict=dict()
    word_set = set(str1).union(set(str2))
    i=0
    for word in word_set:
        word_dict[word] = i
        i += 1
    s1_cut_code = [0] * len(word_dict)
    for word in str1:
        s1_cut_code[word_dict[word]] += 1
    s2_cut_code = [0] * len(word_dict)
    for word in str2:
        s2_cut_code[word_dict[word]] += 1
    # 计算余弦相似度
    sum,sq1,sq2= 0,0,0
    for i in range(len(s1_cut_code)):
        sum += s1_cut_code[i] * s2_cut_code[i]
        sq1 += pow(s1_cut_code[i], 2)
        sq2 += pow(s2_cut_code[i], 2)
    try:
        result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
    except ZeroDivisionError:
        result = 0.0
    #print(result)
    return result

#计算得分
def score(data):
    t=((now-datetime.datetime.strptime(data['time'], '%Y-%m-%d %H:%M:%S')).days*3600*24\
         +(now-datetime.datetime.strptime(data['time'], '%Y-%m-%d %H:%M:%S')).seconds)/3600
    #按小时算
    w=data["likes"]*1+data["replies"]*10+data["retweets"]*5
    return (w+100)*pow(e,(-0.046*t))#24小时候后热度降低至1/3
    #return (w+100)*pow(e,(-0.069*t))#24小时候后热度降低至1/10

#合并所有重复新闻热度并去掉重复新闻
def final(nn):
    n=0
    new_datas=[]
    while n<len(datas):
        start=n
        while n+1<len(datas) and datas[n]['flag']==datas[n+1]['flag']:
            n+=1
        n += 1
        #new_data=min((x for x in datas[start:n]),key=lambda x:datetime.datetime.strptime(x['time'], '%Y-%m-%d %H:%M:%S'))
        # 取时间最早的一个新闻标题
        new_data = max((x for x in datas[start:n]),
                       key=lambda x: x['score'])
        #取分数最高的一个
        new_data['score']=sum(x['score'] for x in datas[start:n])
        # 合计分数
        new_data['from']=" | ".join(set(x['from'] for x in datas[start:n]))
    return new_datas

#加载数据同时计算得分
def load_datas(path):
    source = os.listdir(path)[0]
    # 文件夹内仅保留一个excel
    file_path = os.path.join(path, source)
    fp = open_workbook(file_path)
    table = fp.sheets()[0]
    nrows = table.nrows
    keys = table.row_values(0)
    for n in range(1, nrows):
        datas.append(dict(zip(keys, table.row_values(n))))
        datas[n - 1]['score'] = score(datas[n - 1])
#初始flag为1,2,3....
#用于计算相似度，被判断为同一个新闻的flag会设为一致，只有不同新闻来源的新闻才可以被认定为同一新闻
def Statistics():
    attached = len(datas) * [(0, None, None)]  # 依次为相似度，data_a新闻来源，data_a新闻下标
    for index_a, data_a in enumerate(tqdm.tqdm(datas)):
        if not attached[index_a][0]:
            best_match = (0, None)  # 依次为相似度，data_b新闻下标
            for index_b, data_b in enumerate(datas):
                if data_a['from'] != data_b['from'] and \
                        (temp := similary(extract(data_a['text']), extract(data_b['text']))) > best_match[0]:
                    best_match = (temp, index_b)
            if best_match[0] > similarity:
                if attached[best_match[1]][0] == 0:
                    datas[index_a]['flag'] = best_match[1]
                    attached[best_match[1]] = (best_match[0], data_a['from'], index_a)
                elif attached[best_match[1]][1] != data_a['from']:
                    datas[index_a]['flag'] = best_match[1]
                    attached[best_match[1]] = (best_match[0], data_a['from'], index_a)
                elif attached[best_match[1]][1] == data_a['from'] and best_match[0] > attached[best_match[1]][0]:
                    data_a['flag'] = datas[best_match[1]]['flag']
                    datas[attached[best_match[1]][2]]['flag'] = attached[best_match[1]][2]
                    attached[best_match[1]] = (best_match[0], data_a['from'], index_a)



if __name__ == "__main__":
    for nn,dir in enumerate(datadir):
        datas = []
        load_datas(dir)
        if len(datas)>1000:
            datas=sorted(datas,reverse=True,key=lambda x: x['score'])[:int(len(datas)/3)]
            #数据过多的话，切片取前1/3进行处理，实测热度新闻极度集中
            datas.sort(key=lambda x: x['flag'])
        Statistics()
        datas.sort(key=lambda x: x['flag'])
        datas = final(nn)
        datas=sorted(datas,reverse=True,key=lambda x: x['score'])[:30]
        for n in range(30):
            try:
                datas[n]['url'] = get_url(datas[n], nn)
                print("{}:".format(n), datas[n]['url'])
            except:
                datas[n]['url'] = ""
                print("Get nothing")
            #获得url
        print(datas[:10])
        wb = workbook.Workbook()  # 创建Excel对象
        ws = wb.active  # 获取当前正在操作的表对象
        # 往表中写入标题行,以列表形式写入！
        ws.append(["tweet_id", 'tweet_url', "time", "text", "from", "replies", "retweets", "likes", "url", 'flag', 'score'])
        for data in datas:
            ws.append([data["tweet_id"], data['tweet_url'], data["time"], data["text"], data['from'],
                       data["replies"], data["retweets"], data["likes"], data["url"], data['flag'], data['score']])
        file_path = os.path.join(dir, '{}_flagged.xlsx'.format(dir))
        wb.save(file_path)




        #         if data_a['from']!=data_b['from'] and data_b['flag']==1:
        #             similarity=similary(extract(data_a['text']), extract(data_b['text']))
        #             if similarity<0.2:
        #                 sim['1'].append((data_a['text'],data_b['text'],similarity))
        #             elif similarity < 0.4:
        #                 sim['2'].append((data_a['text'], data_b['text'],similarity))
        #             elif similarity < 0.6:
        #                 sim['3'].append((data_a['text'], data_b['text'],similarity))
        #             elif similarity < 0.8:
        #                 sim['4'].append((data_a['text'], data_b['text'],similarity))
        #             else:
        #                 sim['5'].append((data_a['text'], data_b['text'],similarity))
        # data_a['flag']=0





