"""
Author: Sedem Quame Amekpewu
Date: Saturday, 23rd January 2021
Description: Script for getting categorical information on products from the browngh servers.
"""
import requests
import pprint
import datetime
from scraper_utils import ScraperUtils
from newsfoldr_telegram_bot import sendArticle
utils = ScraperUtils()


def findNavigation(link):
    parsedPage = utils.requestPage(link)
    navigation = parsedPage.select("#menu-main-menu-1")
    # find all anchor tags
    return navigation[0].find_all('a')


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
        header = parsedPage.select("header.td-post-title")[0]

        #article title
        title = header.select("h1")[0].string

        #article category
        category = parsedPage.select(".entry-category")[0].find("a").string

        # article subCategory
        subCategory = ""

        #article author
        author = parsedPage.select(".td-post-author-name")[0].find("a").string

        #article story_date
        story_date = parsedPage.select(".td-post-date")[0].find("time").string
        browngh_date_format = story_date.split(", ")
        year = browngh_date_format[1]
        month = datetime.datetime.strptime(browngh_date_format[0].split(" ")[0], "%B").month
        day = browngh_date_format[0].split(" ")[1]
        news_foldr_date_format = f"{year}-{month}-{day}"

        #article paragraphs
        mainContent = parsedPage.select("div.td-ss-main-content")[0]
        post_content = mainContent.select(".td-post-content")[0]
        paragraphs = getParagraphText(post_content.find_all("p"))

        #article image_url
        image = parsedPage.select(".td-post-featured-image")[0].find(
            "img")["src"]

        #getting youtube links
        youtube = ""
        try:
            youtube = parsedPage.select("iframe")[0]["src"]
        except:
            # do nothing
            print()

        # creating an object in python.
        data = {
            'source': "BrownGh.com",
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


def scrapePage(link, hasPaginatedLinks, isArticle):
    if (utils.checkIfAlreadyScraped(link)):
        return False
    parsedPage = utils.requestPage(link)
    articleContainers = parsedPage.select(".td-module-image")
    if (isArticle):
        for container in articleContainers:
            scrapeArticle(container.find("a")["href"])
    if (hasPaginatedLinks):
        extractPaginated(link)
    # register visited link
    utils.registerScrapedLink(link)


def extractPaginated(link):
    # check if link is in the list of paginated pages, already recorded.
    parsedPage = utils.requestPage(link)
    paginatedLinkContainer = parsedPage.select(".page-nav")
    try:
      if len(paginatedLinkContainer) != 0:
          firstPage = 1
          lastPage = int(paginatedLinkContainer[0].select(".last")[0].string)
          for currentPage in range(firstPage, (lastPage + 1)):
              # iterate through range of paginated pages
              if (not utils.checkIfAlreadyScraped(currentPage)):
                  scrapePage(f"{link}page/{currentPage}", False, True)
                  # register visited paginated page
                  utils.registerScrapedLink(currentPage)
    except:
      print("Something went wrong!")
      


def brown():
    print("starting ...")
    try:
        # import pdb; pdb.set_trace()
        navigationAnchorLinks = findNavigation("https://www.browngh.com/")
        for link in navigationAnchorLinks[0:5]:
            scrapePage(link['href'], True, False)
    except requests.HTTPError as e:
        print(e)

brown()  