from flask import Flask
from flask import  request,render_template
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
#NOTE: div classes provided here to be updated if they are updated by flipkart

app = Flask(__name__)
reviews=[]
flipkart='https://www.flipkart.com'
flipkart_search='https://www.flipkart.com/search?q='

@app.route('/')
def index():
  return render_template('index.html')#Home Page


@app.route('/scraper',methods=['POST'])
def scrapper():
   if request.method=='POST':#if request method is post
       query = flipkart_search + request.form.get('query').replace(" ",'')# Retriving the name
       if len(request.form.get('totalnum'))>0:#Total Number of search results to be performed
           totalnum=int(request.form.get('totalnum'))
       else:
           totalnum = 10# Default search results
       try:
            flipkartPage = urlopen(query)#opening flipkart page
            flipkartPage = flipkartPage.read()
            flipkart_html = bs(flipkartPage, "html.parser")
            urls = flipkart_html.find_all('div', {"class": "_2kHMtA"})  # finding the div class value of the name provided in flipkart page
            url = flipkart_search + urls[0].a['href']
            url_html = urlopen(url).read()
            bs_data = bs(url_html, 'html.parser')
            res = bs_data.find_all('div', {"class": "_1AtVbE col-12-12"})
            k = res[-4].find_all('a')[-1]
       except:
           return "Please Verify the product name"

       review_page = 'https://www.flipkart.com' + k['href']#All reviews page link
       main_review = urlopen(review_page).read()
       bs_main_review = bs(main_review, "html.parser")
       main_review_classes = bs_main_review.find_all('div', {"class": "_1AtVbE col-12-12"})
       Next = flipkart + main_review_classes[-1].find_all('a')[-1]['href']# finding next page link
       res = bs_main_review.find_all('div', {"class": "col _2wzgFH K0kLPL"})# div class with review details
       while len(reviews) < totalnum:#condition to check the total number of reviews is less than specified number
           for i in res:# looping over review div class elements in each page
               if len(reviews) == totalnum:#condition to check if length of obtained reviews is equal to specified number
                   break;#if True then exit the loop
               else:

                   try:
                       if i.find('div', '_3LWZlK _1BLPMq') != None:# condition to check if rating is provided
                           star = i.find('div', '_3LWZlK _1BLPMq').text # Assigning the rating given by user(div class with positive rating)
                       elif i.find('div', '_3LWZlK _1rdVr6 _1BLPMq') != None:
                           star = i.find('div', '_3LWZlK _1rdVr6 _1BLPMq').text#div class with 1 star rating
                       elif i.find('div', '_3LWZlK _32lA32 _1BLPMq') != None:  # 2 & 3 star rating div class
                           star = i.find('div', '_3LWZlK _32lA32 _1BLPMq').text
                   except:
                       star = 'No Rating'#if no rating is provided
                   try:
                       review = i.find('div', 't-ZTKy').div.div.text#Review of the product given by user
                   except:
                       review = 'No Review'#if no review provided
                   try:
                       cust_name = i.find('p', r'_2sc7ZR _2V5EHH').text#Name of the customer
                   except:
                       cust_name = "No Name"
                   try:
                       likes = i.find('div', '_27aTsS').div.span.text#obtained likes for the review
                   except:
                       likes = 0 #if no likes defaults to 0
                   try:
                       dislikes = i.find('div', '_1LmwT9 pkR4jH').span.text# obtained dislikes for the review
                   except:
                       dislikes = 0#if no dislikes then defaults to 0
                   reviews.append({'star': star, 'review': review, 'cust_name': cust_name, 'likes': likes, 'dislikes': dislikes})#adding the dictionary to a list
               next_page = urlopen(Next).read()# opening the next review page
               next_page = bs(next_page, 'html.parser')
               res = next_page.find_all('div', {"class": "col _2wzgFH K0kLPL"})
               next_review_page = next_page.find_all('div', {"class": "_1AtVbE col-12-12"})
               Next = flipkart + next_review_page[-1].find_all('a')[-1]['href']#Updating the Next page
       return render_template('results.html',reviews=reviews)# rendering the output





if __name__ == '__main__':
    app.run(debug=True)
