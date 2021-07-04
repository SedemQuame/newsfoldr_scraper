"""
Author: Sedem Quame Amekpewu
Date: Saturday, 26th June 2021
Description: Script for getting categorical information on products from the newsghana servers.
"""
import requests
import pprint
import datetime
from scraper_utils import ScraperUtils
from newsfoldr_telegram_bot import sendArticle
utils = ScraperUtils()

monthDictionary = {
  "Jan": "January",
  "Feb": "February",
  "Mar": "March",
  "Apr": "April",
  "May": "May",
  "Jun": "June",
  "Jul": "July",
  "Aug": "August",
  "Sep": "September",
  "Oct": "October",
  "Nov": "November",
  "Dec": "December"
}

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
      header = parsedPage.select(".entry-title")[19]
      #article title
      title = str(header.string).strip()

      #article category
      breadCrumbs = (parsedPage.select(".entry-crumbs"))[0].find_all("span")
      # find way to get breadCrumbs number if length is 3.
      category = ""
      subCategory = "Unclassified"

      if(len(breadCrumbs) > 2):
        category = breadCrumbs[1].string
        if(len(breadCrumbs) > 3):
          # article subCategory
          subCategory = breadCrumbs[2].string

      #article author
      author = parsedPage.select(".td-post-author-name")[0].find("a").string

      #article story_date
      newsghana_date_format = (parsedPage.select(".td-module-date")[0].string).replace(",", " ").split(" ")

      year = newsghana_date_format[3]
      month = datetime.datetime.strptime(monthDictionary[newsghana_date_format[0]], "%B").month
      day = newsghana_date_format[1]
      news_foldr_date_format = f"{year}-{month}-{day}"

      # #article paragraphs
      mainContent = parsedPage.select(".td-post-content ")[0].find_all("p")
      paragraphs = getParagraphText(mainContent)

      #article image_url
      image = parsedPage.select(".entry-thumb")[18]["src"]

      #getting youtube links
      youtube = ""

      # creating an object in python.
      data = {
          'source': "Ghanafa.com",
          'title': title,
          'category': category,
          'subCategory': subCategory,
          'author': author,
          'story_date': newsghana_date_format,
          'news_foldr_date_format': news_foldr_date_format,
          'paragraphs': paragraphs,
          'image': image,
          'youtube': youtube,
          'link': link
      }

      # upload data to the mongo db database
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
  articleAnchors = parsedPage.select(".td-image-wrap ")
  for article in articleAnchors[4:-1]:
    scrapeArticle(article['href'])

def getPaginatedLinks(link):
  parsedPage = utils.requestPage(link)
  pages = parsedPage.select(".pages")
  # if length is 0, it's probably a mega-menu
  # ignore for now, and return 0.
  # print(pages)
  if(len(pages) < 1):
    return 0
  else:
    strArr = pages[0].string.split()
    return int(strArr[3].replace(",", ""))
    

def getNavigationLinks(link):
  parsedPage = utils.requestPage(link)
  header = parsedPage.select("#menu-main-menu-1")

  # find all anchors in header
  categoryList = header[0].select("li")
  categoryLinks = []

  for category in categoryList:
    if(category.find("a").get("href") != None):
      categoryLinks.append(category.find("a").get("href"))

  return categoryLinks

def newsghana():
  print("starting ...")
  try:
    links = []
    [links.append(x) for x in getNavigationLinks("https://newsghana.com.gh") if x not in links]

    for link in links:
        max = getPaginatedLinks(link)
        if(max < 1):
          # brainstorm logic for getting data when max is 0
          continue
        else:
          for i in range(max + 1):
            paginatedLinks = "{}page/{}".format(link, i)
            getArticleLinks(paginatedLinks)
  except requests.HTTPError as e:
      print(e)

# newsghana()