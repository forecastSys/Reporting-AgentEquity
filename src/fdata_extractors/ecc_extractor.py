from src.config.config import FMP_API_KEY, ECC_COLLECTION
from src.abstractions import TextDataABC
from src.database import MongoDBHandler
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

class FMPTranscriptFetcher(TextDataABC):
    """
    A simple class to fetch earnings call transcripts from FinancialModelingPrep.
    """

    BASE_URL = "https://financialmodelingprep.com/api/v3/earning_call_transcript"

    def __init__(self):
        """
        Initialize the fetcher with your API key.

        Args:
            api_key (str): Your FinancialModelingPrep API key.
        """
        self.api_key = FMP_API_KEY
        self.col = MongoDBHandler().get_collection(ECC_COLLECTION)

    def fetch(self, ticker: str, year: int, quarter: int) -> dict:
        """
        Fetches the transcript for a given ticker, year, and quarter.

        Args:
            ticker (str): Stock ticker symbol, e.g., "AAPL".
            year (int): Year of the earnings call (e.g., 2020).
            quarter (int): Quarter number (1-4).

        Returns:
            dict: Parsed JSON response from the API.
        """
        url = f"{self.BASE_URL}/{ticker}"
        params = {
            "year": year,
            "quarter": quarter,
            "apikey": self.api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()[0]

    def fetch_from_db(self, ticker: str, year: int, quarter: int) -> dict:

        response = self.col.find(
            {'symbol': ticker,
             'year': year,
             'quarter': quarter}
        )
        response = [i for i in response][0]
        return response