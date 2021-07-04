import os
import requests
from six.moves.urllib.parse import quote


TELEGRAM_TOKEN = "bot1838946203:AAEoFpEsReWMr594zxIKrhepWmqIDsA5aj0"
CHAT_ID= -1001525525139

def formatTelegramMessage(data):
  message = ""

  # send message image

  # append message title
  message += data["title"] + "\n\n"

  # append message body
  paragraphSubArray = data["paragraphs"]
  if len(data["paragraphs"]) > 3:
    paragraphSubArray = data["paragraphs"][0:1]

  visitedFirstParagraph = False
  for paragraph in paragraphSubArray:
    if paragraph != None:
      if paragraph[0].isupper() and visitedFirstParagraph:
        message += ". "
      visitedFirstParagraph = True
      message += paragraph

  # append message youtube links
  message += " ...\n\n"
  if(data["youtube"] != ''):
    message += "Youtube Video Link: " + data["youtube"] + "\n"

  # append article post link
  message += "Read more at\n"
  message += "http://www.newsfoldr.com/article/{}".format(data["title"].replace(" ", "_"))

  return message

def sendArticle(data):
    message = formatTelegramMessage(data)
    final_message = "<b><u>" + data["category"] +"</u></b>\n" + quote(message)

    if(data["youtube"] != ""):
      base_url = "https://api.telegram.org/{}/sendMessage?chat_id={}&parse_mode=HTML&text={}".format(TELEGRAM_TOKEN, CHAT_ID, final_message)
    elif(data["image"] != ""):
      base_url = "https://api.telegram.org/{}/sendPhoto?chat_id={}&photo={}&parse_mode=HTML&caption={}".format(TELEGRAM_TOKEN, CHAT_ID, data["image"],final_message)
    else:
      base_url = "https://api.telegram.org/{}/sendMessage?chat_id={}&parse_mode=HTML&text={}".format(TELEGRAM_TOKEN, CHAT_ID, final_message)

    requests.get(base_url)