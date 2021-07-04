"""
Author: Sedem Quame Amekpewu
Date: Saturday, 23rd January 2021
Description: Script for getting categorical information on products from the peacefm servers.
"""
import requests
import pprint
import datetime
import numpy as np
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

# function to get unique values
def unique(list):
    x = np.array(list)
    return (np.unique(x))


def findNavigation(link):
    navigation = utils.requestPage(link).select(".jeg_menu_style_5")[0]
    # find all anchor tags
    linkLists = []
    for link in navigation.find_all("a")[1:-1]:
        if "#" not in link:
            linkLists.append(f'https://www.peacefmonline.com{link["href"]}')
    return (unique(linkLists[0:-1]))


def getParagraphText(paragraphStr):
    return paragraphStr.split("<br>")[0].split(".")


def scrapeArticle(link):
    try:
        parsedPage = utils.requestPage(f'{link}').select(
            ".jeg_main_content")[0]

        title = parsedPage.select(".jeg_post_title")[0].string

        story_date = parsedPage.select(".jeg_meta_date")[0].string[1:-1]
        peacefm_date_format = story_date.split("-")
        year = peacefm_date_format[2]
        month = datetime.datetime.strptime(monthDictionary[peacefm_date_format[1]], "%B").month
        day = peacefm_date_format[0]
        news_foldr_date_format = f"{year}-{month}-{day}"

        category = parsedPage.select(".jeg_meta_category")[0].select(
            "a")[0].string

        subCategory = ""

        if category == "General News" or category == "Crime":
          category = "Viral"
        elif "ball" in category:
          category = "Sports"
        elif "Economy" in category or "Business" in category or "Banking" in category:
          category = "Business"

        image = parsedPage.select(".wp-image-133")[0]["src"]

        mainContent = parsedPage.select(".content-inner")[0]

        paragraphs = getParagraphText(mainContent.find("p").text)

        author = "peacefmonline"
        youtube = ""
        try:
            author = parsedPage.select(".peace_black_text_4")[0].select(
                "a")[0].string

            youtube = mainContent.select(".youtube-video-container")[0].find(
                "iframe")['src']
        except:
            # do nothing
            print("")

        data = {
            'source': "Peace Fm Online",
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
    # except requests.HTTPError as e:
    #     print(e)
    except Exception as err:
      print(err)


def visitLinksInArchive(link):
    try:
      jegBlockContainer = utils.requestPage(f'{link}').select(
          ".arch_dataTable")[0].find_all("a")

      # print(jegBlockContainer)
      # nestedArchives = []
      for anchor in jegBlockContainer:
          link = f'https://www.peacefmonline.com/{anchor["href"]}'
          # if (link.find("archives") > -1
          #         and not utils.checkIfAlreadyScraped(link)):
              # nestedArchives.append(link)
          if (link.find("archives") > -1):
              getArchiveLinks(link)
              # register visited link
              utils.registerScrapedLink(link)
          else:
              scrapeArticle(link)
    except Exception as e:
      print(e)


def getArchiveLinks(link):
    try:
        archiveTableContainer = utils.requestPage(link).select(
            ".tagcloud")[0].find_all("a")
        for anchor in archiveTableContainer:
            link = f'https://www.peacefmonline.com{anchor["href"]}'
            if("archives" in link):
              visitLinksInArchive(link)
            # else
            if (not utils.checkIfAlreadyScraped(link)):
                if("archives" in link):
                    visitLinksInArchive(link)
                else:
                    scrapeArticle(link)
                # register visited link
                utils.registerScrapedLink(link)
    except IndexError as e:
        print(e)


def peacefm():
    pageLinks = [
      'https://www.peacefmonline.com/pages/business/archives/',
      'https://www.peacefmonline.com/pages/comment/archives/',
      'https://www.peacefmonline.com/pages/local/archives/',
      'https://www.peacefmonline.com/pages/politics/archives/',
      'https://www.peacefmonline.com/pages/showbiz/archives/',
      'https://www.peacefmonline.com/pages/sports/archives/'
    ]
    try:
      for link in pageLinks:
        getArchiveLinks(link)
    except requests.HTTPError as e:
        print(e)

peacefm()