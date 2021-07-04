"""
Author: Sedem Quame Amekpewu
Date: Thursday, 1st June 2021
Description: Script for getting categorical information on products from newsapi. This api will be used to return tech articles
"""
import requests
from scraper_utils import ScraperUtils
from newsfoldr_telegram_bot import sendArticle
utils = ScraperUtils()

API_KEY = "a6a86fbcf32e4e6a9a36bdcd3786b4c9"

def scrapeArticle(article, category):
  try:
    title = article["title"]
    story_date = article["publishedAt"]
    news_foldr_date_format = article["publishedAt"]
    subCategory = ""
    image = article["urlToImage"]
    paragraphs = article["content"]
    author = article["author"]
    youtube = ""

    data = {
        'source': "",
        'title': title,
        'category': category,
        'subCategory': subCategory,
        'author': author,
        'story_date': story_date,
        'news_foldr_date_format': news_foldr_date_format,
        'paragraphs': paragraphs,
        'image': image,
        'youtube': youtube,
        'link': article["url"]
    }

    # upload data to the mongo db database
    utils.uploadToMongoDB(data)
    sendArticle(data)
  except IndexError:
    print(IndexError)
  except Exception as e:
    print(e)

def main():

  categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
  countries = ["ae", "ar", "at","au","be","bg","br","ca","ch","cn","co","cu","cz","de","eg","fr","gb","gr","hk","hu","id","ie","il","in","it","jp","kr","lt","lv","ma","mx","my","ng","nl","no","nz","ph","pl","pt","ro","rs","ru","sa","se","sg","si","sk","th","tr","tw","ua","us","ve","za"]

  for country in countries:
    for category in categories:
      try:
        url = f"https://newsapi.org/v2/everything?country={country}&category={category}&apiKey={API_KEY}"
        articles = requests.get(url).json()
        if articles["status"] == "ok":
          for article in articles["articles"]:
            scrapeArticle(article, category)
        else:
          print(f"Code: {articles['code']}")
          print(f"Message: {articles['message']}\n")
      except Exception as e:
        print(e)

main()