from rcg.code.code import Creds, update_chart
from dotenv import load_dotenv


if __name__ == "__main__":
    """adds new rcg data if it exists"""
    load_dotenv()
    creds = Creds()
    output = update_chart(creds)