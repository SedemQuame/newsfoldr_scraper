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


def getLinkFromInlineCss(Text):
    urlTextStartPosition = (Text.find(" url( ") + 6)
    urlTextEndPosition = Text.find(" );")
    return (Text[urlTextStartPosition:urlTextEndPosition])


def getParagraphText(paragraphArr):
    paragraphs = []
    for para in paragraphArr:
        # print(para.string)
        paragraphs.append(para.string)
    return paragraphs


def scrapeArticle(link):
    try:
        parsedPage = utils.requestPage(link)

        #article title
        title = parsedPage.select(".entry-title")[5].string

        if (title == None):
            #article header
            header = parsedPage.select("header.entry-header")[0]
            title = header.select(".entry-title")[0].string

        #article story_date
        story_date = parsedPage.select(".entry-date")[0].string
        browngh_date_format = story_date.split(", ")
        year = browngh_date_format[1]
        month = datetime.datetime.strptime(browngh_date_format[0].split(" ")[0], "%B").month
        day = browngh_date_format[0].split(" ")[1]
        news_foldr_date_format = f"{year}-{month}-{day}"

        #article paragraphs
        mainContent = parsedPage.select("div.entry-content")[0]
        print(mainContent)
        paragraphs = getParagraphText(mainContent.find_all("p"))
        print(paragraphs)
        

        # article subCategory
        subCategory = ""

        #article image_url
        # image = getLinkFromInlineCss(
        #     parsedPage.select(".entry-media-row-05")[0].select("style")
        #     [0].string)
        image = parsedPage.select(".g1-frame-inner")[5].find("img")["data-srcset"].split(",")[0]


        # get youtube video link
        youtube = ""
        try:
            youtube = parsedPage.select(".mace-youtube")[0]['data-mace-video']
        except:
            # do nothing
            print("")

        # creating an object in python.
        data = {
            'source': "EOnlineGh.com",
            'title': title,
            'category': "Entertainment",
            'subCategory': subCategory,
            'author': " ThePrinceLive",
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


def eonline():
    for i in range(292):
        link = f"https://www.eonlinegh.com/page/{i}"
        # check if page is unvisited
        if (not utils.checkIfAlreadyScraped(link)):
            parsedPage = utils.requestPage(link)
            collectionItems = parsedPage.select(".g1-frame")
            
            for itemLink in collectionItems:
              print(itemLink["href"])
              scrapeArticle(itemLink["href"])
              # register visited paginated page
              utils.registerScrapedLink(itemLink["href"])

eonline()