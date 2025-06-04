from src.config import MONGODB_URI, DB, ECC_COLLECTION
from pymongo import MongoClient
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

class MongoDBHandler:

    def __init__(self):
        super().__init__()
        self.DB_URI = MONGODB_URI
        self.client = MongoClient(self.DB_URI)

    def get_database(self, DB=DB):
        """
        :param DB: Your mongodb database, default is local
        """
        db = self.client[DB]
        return db

    def get_collection(self, COLLECTION):

        db = self.get_database(DB)
        col = db[COLLECTION]
        return col