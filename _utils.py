"""
Mikeal888

This file contains utility functions for the project.

"""

from newsapi import NewsApiClient
from pymongo import MongoClient
from datetime import datetime


class GetNews:
    """
    This class contains methods for getting news from the NewsAPI.


    """

    def __init__(self, api, query, start=None, end=None) -> None:
        """
        Initializes the class with the query and the start and end dates.
        If no start and end dates are given, the default is the current date.
        """

        self.query = query
        self.api = NewsApiClient(api_key=api)
        self.start = start
        self.end = end
        self.news_list = self.get_articles()

        # Set the start and end dates to the current date if they are not given
        if self.start == None:
            self.start = datetime.today().strftime("%Y-%m-%d")
        if self.end == None:
            self.end = datetime.today().strftime("%Y-%m-%d")

        # raise exception if the start date is after the end date
        if self.start > self.end:
            raise Exception("Start date cannot be after end date.")

    def get_articles(self) -> list:
        """
        Returns a list of articles from the NewsAPI.
        """

        articles = self.api.get_everything(
            q=self.query,
            from_param=self.start,
            to=self.end,
            language="en",
            sort_by="relevancy",
        )["articles"]

        # Turn the articles into a list of dictionaries
        self.news_list = []
        for article in articles:
            # Skip articles that do not have a source
            if (article["source"]["id"] == None) and (
                article["source"]["name"] == None
            ):
                continue

            # Add the article to the list
            self.news_list.append(
                {
                    "title": article["title"],
                    "media": article["source"]["name"],
                    "date": article["publishedAt"][:10],
                    "url": article["url"],
                }
            )

        return self.news_list

    def add_to_db(self, api, db_name, collection_name):
        """
        Adds the articles to the MongoDB database.
        """
        # Connect to the MongoDB database
        client = MongoClient(api)
        db = client[db_name]
        collection = db[collection_name]

        # Add the articles to the database
        collection.insert_many(self.news_list)

        # find any added duplicates and remove them
        duplicates = collection.aggregate(
            [
                # group on title and media
                {"$group": {"_id": "$title", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}},
            ]
        )

        # delete the duplicates
        for doc in duplicates:
            title = doc["_id"]
            collection.delete_one({"title": title})

        # Close the connection to the database
        client.close()
