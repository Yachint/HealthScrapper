import datetime
import time, threading
from newspaper import Article
from bs4 import BeautifulSoup
import requests
import re
import pymongo

_id = 0
entry = {}


def clean_text(test_str):
    ret = ''
    skip1c = 0
    skip2c = 0
    for i in test_str:
        if i == '[':
            skip1c += 1
        elif i == '(':
            skip2c += 1
        elif i == '-':
            skip2c += 1
        elif i == ']' and skip1c > 0:
            skip1c -= 1
        elif i == ')' and skip2c > 0:
            skip2c -= 1
        elif i == '\n' and skip2c > 0:
            skip2c -= 1
        elif skip1c == 0 and skip2c == 0:
            ret += i
    return ret


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def get_symptoms(web_url):
    more_symp = []
    r = requests.get(web_url)

    data = r.text
    j = []

    mystring = ""
    soup = BeautifulSoup(data, 'html.parser')
    # print(cleanhtml(str(soup.title)).split(":", maxsplit=1)[0])
    result = soup.find_all("h2", {"itemprop": "alternativeHeadline"})
    key = 0
    for res in result:
        mystring += res.text
        if key != 0:
            j.append(res.text)
        key += 1

    h = []
    temp_string = ""
    soup_new = BeautifulSoup(data, 'html.parser')
    result = soup_new.find_all("div", {"class": "Tab_Items"})
    key = 0
    for res in result:
        if key != 0:
            temp_string += res.text
            # print(re.split("--",temp_string.replace('\n', '--')))
            h = re.split("--", temp_string.replace('\n', '--'))
            while '' in h:
                h.remove('')
            # x = clean_text(temp_string)
            # print(x)
            # x = x.replace('\n','')
            # h = x.split()
        key += 1

    # FOR EXTRA SIMILAR CAUSES-----------------------------------------------------------------------------------
    get_text = soup_new.find_all("div", {"class": "Tab_Items"})
    for t in get_text:
        # print(list(str(t.text)))
        # print(str(t.text).count('\r'))
        if str(t.text).count('\r') > 2:
            more_symp = re.split("--", ((str(t.text).strip()).replace('\r', '--')).replace('\n', ''))
            # print('going r')
        else:
            more_symp = re.split('--', (str(t.text).strip()).replace('\n', '--'))
            # print('going normal')
        # print(re.split("--", ((str(t.text).strip()).replace('\n','--'))))
        # print(re.split("--", ((str(t.text).strip()).replace('\r', '--')).replace('\n','')))
        break

    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # ' '.join(mystring.split())
    # re.sub('\s+', ' ', mystring).strip()
    # mystring.replace(" ", "")
    cause_array = j
    # print(j)

    # print(h)

    cause_link_array = []
    gug = ""

    for link in soup.find_all("div", {"class": "apPage article-extra"}):
        links = link.find_all('a')
        for b in links:
            # print(b.get('href'))
            gug = str(b.get('href'))
            if gug != 'None':
                cause_link_array.append(gug)

    # print(cause_link_array)

    my_dict = {}

    links_new = cause_link_array[:len(cause_array)]

    size = len(cause_array)
    for i in range(0, size):
        my_dict[cause_array[i]] = links_new[i]

    # print(my_dict)

    global _id
    _id += 1
    entry['_id'] = _id
    entry['name'] = cleanhtml(str(soup.title)).split(":", maxsplit=1)[0]
    entry['causes'] = my_dict
    entry['medication'] = h
    if len(my_dict) == 0:
        entry['similar'] = more_symp
    # print(entry)
    print(entry['name'])
    try:
        print(entry['similar'])
    except:
        print('No extra Similar Causes!')

    # CLEAR ALL
    my_dict.clear()
    more_symp.clear()


def parse_symptoms_webpage(web_url2):
    r2 = requests.get(web_url2)

    data2 = r2.text
    soup = BeautifulSoup(data2, 'html.parser')

    q = []
    bip = ""
    for link in soup.find_all("div", {"class": "AZ_results"}):
        links = link.find_all('a')
        for b in links:
            # print(b.get('href'))
            bip = str(b.get('href'))
            if bip != 'None':
                bip = "https://www.rxlist.com" + bip
                q.append(bip)

    q.pop(0)
    print(q)
    for link in q:
        get_symptoms(link)
    # soup.find_all("a", class_="apPage")


def put_in_database(entry):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["RxList"]
    mycol = mydb["Symptoms"]

    x = mycol.insert(entry)


web_url2 = "https://www.rxlist.com/symptoms_and_signs/alpha_a.htm"
# web_url = "https://www.rxlist.com/abscessed_tooth_symptoms_and_signs/symptoms.htm"
web_url = "https://www.rxlist.com/alcohol_withdrawal_symptoms_and_signs/symptoms.htm"
# web_url = "https://www.rxlist.com/ankle_pain/symptoms.htm"
# web_url = "https://www.rxlist.com/adhd_symptoms_and_signs/symptoms.htm"

# parse_symptoms_webpage(web_url2)
get_symptoms(web_url)
