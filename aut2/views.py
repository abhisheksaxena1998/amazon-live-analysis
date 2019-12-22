def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
import warnings 
import pandas as pd
import numpy as np
from sklearn.externals import joblib
from lxml import html
from json import dump,loads
from requests import get
import json
import csv
from re import sub
from dateutil import parser as dateparser
from time import sleep
from django.http import HttpResponse
from django.shortcuts import render
import os

def home(request):
    return render(request,'home.html')

def result(request):
    #nm="amazonextraction\\az_joy_corpus.txt" #request.GET['url']
    #"az_joy_corpus.txt"
    nm=request.GET['url']
    csvfilename=nm[23:28]+".csv"

    imgname=nm[23:28]+'.png'
    location="static\\"+imgname
    loc="/static/"+imgname
    print (loc)
    l=f'\"{loc}"'
    print (l)
    print (location)

    #if os.path.exists("static\\cloud_amazon3.png"):
    #    os.remove("static\\cloud_amazon3.png")
    #else:
    #    print("The file does not exist")
    #nm="amazonextraction/" + nm
    
    def ParseReviews(i):
        amazon_url  = nm
        
        #amazon_url  = f'https://www.amazon.in/JBL-Ultra-Portable-Wireless-Bluetooth-Speaker/product-reviews/B07B9NMQTP/ref=cm_cr_arp_d_paging_btm_next_2?pageNumber={i}'
        #gen sample https://www.amazon.in/Infinity-Glide-100-Sweatproof-Headphones/product-reviews/B07WBY3HNV/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews
        #https://www.amazon.in/Godrej-Split-1-5T-GIC18-GWQG/product-reviews/B07L8YHCDT/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber={i}
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        for i in range(5):
            response = get(amazon_url, headers = headers, verify=False, timeout=30)
            if response.status_code == 404:
                return {"url": amazon_url, "error": "page not found"}
            if response.status_code != 200:
                continue
            
            
            cleaned_response = response.text.replace('\x00', '')
            
            parser = html.fromstring(cleaned_response)
            XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
            XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
            XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'
            XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
            XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
            XPATH_PRODUCT_PRICE = '//span[@id="priceblock_ourprice"]/text()'

            raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
            raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
            total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
            reviews = parser.xpath(XPATH_REVIEW_SECTION_1)

            product_price = ''.join(raw_product_price).replace(',', '')
            product_name = ''.join(raw_product_name).strip()

            if not reviews:
                reviews = parser.xpath(XPATH_REVIEW_SECTION_2)
            ratings_dict = {}
            reviews_list = []

            
            for ratings in total_ratings:
                extracted_rating = ratings.xpath('./td//a//text()')
                if extracted_rating:
                    rating_key = extracted_rating[0] 
                    raw_raing_value = extracted_rating[1]
                    rating_value = raw_raing_value
                    if rating_key:
                        ratings_dict.update({rating_key: rating_value})
            
            
            for review in reviews:
                XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
                XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
                XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'
                XPATH_REVIEW_TEXT_1 = './/div[@data-hook="review-collapsed"]//text()'
                XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
                XPATH_REVIEW_COMMENTS = './/span[@data-hook="review-comment"]//text()'
                XPATH_AUTHOR = './/span[contains(@class,"profile-name")]//text()'
                XPATH_REVIEW_TEXT_3 = './/div[contains(@id,"dpReviews")]/div/text()'
                
                raw_review_author = review.xpath(XPATH_AUTHOR)
                raw_review_rating = review.xpath(XPATH_RATING)
                raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
                raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
                raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
                raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
                raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)

                # Cleaning data
                author = ' '.join(' '.join(raw_review_author).split())
                review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
                review_header = ' '.join(' '.join(raw_review_header).split())

                try:
                    review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
                except:
                    review_posted_date = None
                review_text = ' '.join(' '.join(raw_review_text1).split())

                # Grabbing hidden comments if present
                if raw_review_text2:
                    json_loaded_review_data = loads(raw_review_text2[0])
                    json_loaded_review_data_text = json_loaded_review_data['rest']
                    cleaned_json_loaded_review_data_text = re.sub('<.*?>', '', json_loaded_review_data_text)
                    full_review_text = review_text+cleaned_json_loaded_review_data_text
                else:
                    full_review_text = review_text
                if not raw_review_text1:
                    full_review_text = ' '.join(' '.join(raw_review_text3).split())

                raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
                review_comments = ''.join(raw_review_comments)
                review_comments = sub('[A-Za-z]', '', review_comments).strip()

                with open (csvfilename,'a',encoding="utf-8") as res:        
                    writer=csv.writer(res)           
                    s="{},{},{},{}\n".format(review_posted_date,review_header,review_rating,author)
                    res.write(s)
                    print (s)

                review_dict = {
                                    'review_comment_count': review_comments,
                                    'review_text': full_review_text,
                                    'review_posted_date': review_posted_date,
                                    'review_header': review_header,
                                    'review_rating': review_rating,
                                    'review_author': author

                                }
                reviews_list.append(review_dict)
        
            
            data = {
                        'ratings': ratings_dict,
                        'reviews': reviews_list,
                        'url': amazon_url,
                        'name': product_name,
                        'price': product_price
                    
                    }
            return data

        return {"error": "failed to process the page", "url": amazon_url}
                

    def ReadAsin():
        # Add your own ASINs here
        extracted_data = []
        
        for i in range(5):
            print(f"Downloading and processing page {i}")
            extracted_data.append(ParseReviews(i))
            sleep(5)
        f = open('buggdata.json', 'w')
        dump(extracted_data, f, indent=4)
        f.close()







    ReadAsin()

    df=pd.read_csv(csvfilename,error_bad_lines=False)
    df.columns=['review_posted_date','review_header','review_rating','author']
    X=df['review_header']

    import re  


    processed_tweets=[]

    for tweet in range(0, len(X)):  
        processed_tweet = re.sub(r'\W', ' ', str(X[tweet]))

                
        # Remove all the special characters
        
        processed_tweet = re.sub(r'http\S+', ' ', processed_tweet)
        
        #processed_tweet = re.sub(r'https?:\/\/+', ' ', processed_tweet)
        
        #processed_tweet=re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', ' ',processed_tweet)
        
        processed_tweet=re.sub(r'www\S+', ' ', processed_tweet)
        
        processed_tweet=re.sub(r'co \S+', ' ', processed_tweet)
        # remove all single characters
        processed_tweet = re.sub(r'\s+[a-zA-Z]\s+', ' ', processed_tweet)
    
        # Remove single characters from the start
        processed_tweet = re.sub(r'\^[a-zA-Z]\s+', ' ', processed_tweet) 
    
        # Substituting multiple spaces with single space
        processed_tweet= re.sub(r'\s+', ' ', processed_tweet, flags=re.I)
    
        # Removing prefixed 'b'
        processed_tweet = re.sub(r'^b\s+', ' ', processed_tweet)
        
        processed_tweet = re.sub(r'\d','',processed_tweet)
        
        processed_tweet= re.sub(r'\s+', ' ', processed_tweet, flags=re.I)

    
        # Converting to Lowercase
        processed_tweet = processed_tweet.lower()
        
        processed_tweets.append(processed_tweet)

    with open('az_off_corpus.txt', 'w',encoding='utf-8') as f:
        for item in processed_tweets:
            f.write("%s\n" % item)    
        

    sample = open("az_off_corpus.txt", "r",encoding='utf-8') 
    s = sample.read() 

    # Replaces escape character with space 
    f = s.replace("\n", " ") 

    from os import path
    from PIL import Image
    from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
    import matplotlib.pyplot as plt
    #% matplotlib inline
    stopwords= set(STOPWORDS)

    stopwords.update(["status","still","must","support","",'pretty','mmine','loud','amazon','stays','anything','mine','month','proper','listen','written','box' ,"public","last","read","johnson","didn","ve","put","needs","save","help","deal","tories","years","articles","need","back","government","pm","back","life","care","everyone","give","day","country","new","look","mps","everything","really","need","hard","believe","even","still","re","eu","pic","dlidington", "philiphammonduk","jeremy_hunt","may","theresa_may","alanduncanmp","watson","work",'don', "anna_soubry","voted","heidi","constituents","heidiallen","claiming","yasmin","george_osborne","ayeshahazarika","tom","conservatives","griffith","hear","tory", "twitter","amberrudduk","love","take","real","friend","good","conservative","election","right","tell","vote","sure","parliament",'people',"justinegreening","tom_watson","labour","time","party","think","going","set","lines","nickymorgan","amberruddhr","will","one","brexit","say","mp","said","want","come","well","no","see","now","know","borisjohnson","stephentwigg","please","happy","share","remember","thank","much","constituent","spaces","job","action","got","jbl",'sound','product','speaker','rha','gya','high','hai',"today",'ho','go','ll','amazes','working','thing','laptop','gaya','raha','purchase','bluetooth','speakers','amazing','compactness','connect'])

    wordcloud = WordCloud(
                            background_color='black',
                            stopwords=stopwords,
                            max_words=200,
                            max_font_size=150, width=1000, height=450,
                            random_state=42
                            ).generate(f)
    print(wordcloud)
    plt.figure(figsize = (10, 10), facecolor = None) 
    fig = plt.figure(1)
    plt.imshow(wordcloud)
    plt.tight_layout(pad=0)

    plt.axis('off')
    plt.show()
    fig.savefig(location, bbox_inches='tight')
    fig.savefig(imgname, bbox_inches='tight')
    plt.savefig('static\\cloud_amazon.png', facecolor='k', bbox_inches='tight')


    return render(request,'result.html',{'result':'Real-time analysis successfull','url':nm,'filename':loc,'f2':imgname})

def about(request):
    return render(request,'about.html')    