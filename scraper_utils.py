import requests
from pymongo import MongoClient
from firebase import firebase
from bs4 import BeautifulSoup


class ScraperUtils:
    def __init__(self):
        self.database_password = "hhkaT54Qf3733iQ"
        self.database_name = "aggregatr"
        self.database_mongo_client = MongoClient(
            f"mongodb+srv://aggregatr_admin:{self.database_password}@aggregatr.op7su.mongodb.net/{self.database_name}?retryWrites=true&w=majority"
        )
        self.mongo_database_connection = self.database_mongo_client['docs']
        self.database_firebase_client = "https://aggregatr-7c2b7-default-rtdb.firebaseio.com/"

    def uploadToFirebase(self, data):
        firebase_connection = firebase.FirebaseApplication(
            self.database_firebase_client, None)
        print(firebase_connection.post('/articles', data))

    def alreadyExists(self, Link):
        if (self.mongo_database_connection.articles.find({
                'link': Link
        }).count() > 0):
            return True
        return False

    def uploadToMongoDB(self, data):
        #check if document alreadyExists
        if not self.alreadyExists(data['link']):
            print('One post: {0}'.format(self.mongo_database_connection.articles.insert_one(data).inserted_id))

    def requestPage(self, Link):
        #request link
        #parse response to beautiful soup
        resp = requests.get(Link, timeout=45)
        return BeautifulSoup(resp.text, 'lxml')

    def checkIfAlreadyScraped(self, Link):
        if (self.mongo_database_connection.scrapedLinks.find({
                'link': Link
        }).count() > 0):
            return True
        return False

    def registerScrapedLink(self, link):
        print('Visited link: {}\nPost id:{}'.format(
            link,
            self.mongo_database_connection.scrapedLinks.insert_one({
                "link": link
            }).inserted_id))