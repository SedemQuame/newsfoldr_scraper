"""
Author: Sedem Quame Amekpewu
Date: Saturday, 25th June 2021
Description: Script for getting categorical information on products from the gfa servers.
"""
import requests
import pprint
import datetime
from scraper_utils import ScraperUtils
from newsfoldr_telegram_bot import sendArticle
utils = ScraperUtils()

def getParagraphText(paragraphArr):
    paragraphs = []
    for para in paragraphArr:
        paragraphs.append(para.string)
    return paragraphs

def scrapeArticle(link):
  if (utils.checkIfAlreadyScraped(link)):
        return False

  try:
      #scrape and store data in firebase
      parsedPage = utils.requestPage(link)

      #article header
      header = parsedPage.select(".article-title")[0]
      #article title
      title = str(header.string).strip()

      #article category
      category = "Sports"

      # article subCategory
      subCategory = "Football"

      #article author
      author = "ghanafa"

      #article story_date
      story_date = parsedPage.select(".time")[0].string
      # year = browngh_date_format[1]
      # month = datetime.datetime.strptime(browngh_date_format[0].split(" ")[0], "%B").month
      # day = browngh_date_format[0].split(" ")[1]
      news_foldr_date_format = f"{0}-{0}-{0}"

      # #article paragraphs
      mainContent = parsedPage.select(".article__container")[0].find_all("div")[4]
      # post_content = mainContent.select(".td-post-content")[0]
      paragraphs = getParagraphText(mainContent.find_all("p"))

      #article image_url
      image = parsedPage.select(".responsive-image")[0].find("img")["src"]

      #getting youtube links
      youtube = ""

      # creating an object in python.
      data = {
          'source': "Ghanafa.com",
          'title': title,
          'category': category,
          'subCategory': subCategory,
          'author': author,
          'story_date': story_date,
          'news_foldr_date_format': news_foldr_date_format,
          'paragraphs': paragraphs,
          'image': image,
          'youtube': youtube,
          'link': link
      }

      # # upload data to the mongo db database
      utils.uploadToMongoDB(data)
      pprint.pprint(data)

      sendArticle(data)
  except IndexError:
    print(IndexError)
  except requests.HTTPError as e:
      print(e)
  finally:
      # register visited link
      # utils.registerScrapedLink(link)
      pass

def getArticleLinks(paginatedLinks):
  # get all anchor links with class ".fa-content-promo__block-link"
  parsedPage = utils.requestPage(paginatedLinks)
  articleAnchors = parsedPage.select(".fa-content-promo__block-link")
  for articles in articleAnchors:
    scrapeArticle(articles['href'])

def ghanafa():
  print("starting ...")
  try:
      for i in range(411):
        paginatedLinks = "https://www.ghanafa.org/category/news?page={}".format(i)
        getArticleLinks(paginatedLinks)
  except requests.HTTPError as e:
      print(e)

ghanafa()