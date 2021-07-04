"""
Author: Sedem Quame Amekpewu
Date: Saturday, 23rd January 2021
Description: Script for getting categorical information on products from the myjoyonline servers.
"""
import requests
import pprint
import datetime
from scraper_utils import ScraperUtils
from newsfoldr_telegram_bot import sendArticle
utils = ScraperUtils()

def extractLinkFrom(anchor):
    return anchor["href"]

def findNavigation(link):
    print(link)
    parsedPage = utils.requestPage(link)
    navigation = parsedPage.select("#menu-top-menu")
    # find all anchor tags
    return list(map(extractLinkFrom, navigation[0].find_all('a')))


def getLinkFromInlineCss(Text):
    urlTextStartPosition = (Text.find(" url( ") + 6)
    urlTextEndPosition = Text.find(" );")
    return (Text[urlTextStartPosition:urlTextEndPosition])


def getParagraphText(paragraphArr):
    paragraphs = []
    for para in paragraphArr:
        paragraphs.append(para.string)
    return paragraphs


def scrapeArticle(link, category, subCategory):
    try:
        #scrape and store data in firebase
        parsedPage = utils.requestPage(link)

        #article header
        header = parsedPage.select(".article-title a h1")[0]

        #article title
        title = header.string

        # article author
        author = parsedPage.select(".article-meta a")[0].string

        #article story_date
        story_date = parsedPage.select(".article-meta div")[0].text
        myjoyonline_date_format = story_date.split(" ")
        year = myjoyonline_date_format[3]
        month = datetime.datetime.strptime(myjoyonline_date_format[2], "%B").month
        day = myjoyonline_date_format[1]
        news_foldr_date_format = f"{year}-{month}-{day}"

        #article paragraphs
        paragraphs = parsedPage.select("#article-text p")

        #article image_url
        image = parsedPage.select(".bgposition")[0].attrs["data-src"]

        #getting youtube links
        youtube = ""
        try:
            youtube = parsedPage.select("iframe")[0]["src"]
        except:
            # do nothing
            print()

        # creating an object in python.
        data = {
            'source': "myjoyonline.com",
            'title': title,
            'category': category.capitalize(),
            'subCategory': subCategory,
            'author': "myjoyonline",
            'story_date': story_date[1:],
            'news_foldr_date_format': news_foldr_date_format,
            'paragraphs': getParagraphText(paragraphs),
            'image': image,
            'youtube': youtube,
            'link': link
        }

        # upload data to the mongo db database
        utils.uploadToMongoDB(data)
        pprint.pprint(data)

        sendArticle(data)
    except IndexError as e:
        print(e)
    except requests.HTTPError as e:
        print(e)
    finally:
        pass


def scrapePage(link, hasPaginatedLinks, isArticle, category, subCategory):
    parsedPage = utils.requestPage(link)
    articleContainers = parsedPage.select(".home-section-story-list")
    for container in articleContainers:
        scrapeArticle(container.find("a")["href"], category, subCategory)


def extractPaginated(link, category, subCategory):
    # check if page is unvisited
    if (not utils.checkIfAlreadyScraped(link)):
        paginatedLinkContainer = utils.requestPage(link).select(
            ".page-numbers")
        if len(paginatedLinkContainer) != 0:
            # page ranges.
            firstPage = 1
            lastPage = int(paginatedLinkContainer[-2].string.replace(",", ""))
            for page in range(firstPage, (lastPage + 1)):
                # check if page is unvisited
                if (not utils.checkIfAlreadyScraped(page)):
                    paginatedLinkPage = f'{link}page/{page}'
                    print(paginatedLinkPage)
                    scrapePage(paginatedLinkPage, False, True, category, subCategory)
                    utils.registerScrapedLink(paginatedLinkPage)
    utils.registerScrapedLink(link)


def findSubCategoryLinks(link):
    #check to see what live is an implement a function suitable to it
    if (link != "/live"):
        subCategories = utils.requestPage(link).select(".home-section-label")
        category = getCategory(link)
        for sub in subCategories:
            subCategory = sub.text[1:]
            pprint.pprint(subCategory)
            if (sub.find("a").attrs.get("href") != ""
                    and sub.find("a").attrs.get("href") != None):
                extractPaginated(sub.find("a").attrs.get("href"), category, subCategory)


def getCategory(link):
    category = link.split("/")[-1]
    if(category == ''):
      category = link.split("/")[-2]
    return category


def myjoyonline():
    # find all links in the navbar
    navigationAnchorLinks = findNavigation("https://www.myjoyonline.com/")[1: -3]
    for link in navigationAnchorLinks:
        findSubCategoryLinks(link)

myjoyonline()