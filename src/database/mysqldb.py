from src.config import OPENAI_API_KEY, MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_PORT
from sqlalchemy import create_engine, text

class MySQLHandler:

    def _get_engine(self):
        engine = create_engine(
            f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}/caesars_reporting_system')
        return engine