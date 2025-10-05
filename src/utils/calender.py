import requests
import datetime
from typing import List

class PublicHolidayUtils:
    def __init__(self, country_code: str):
        """
        Initializes the Public Holiday utility using Nager.Date API.
        :param country_code: Country code for fetching public holidays (e.g., 'US', 'IN')
        """
        self.country_code = country_code
        self.base_url = "https://date.nager.at/api/v3/PublicHolidays"

    def get_public_holidays(self, start_date: datetime.date, end_date: datetime.date) -> List[datetime.date]:
        """
        Fetches public holidays between the given start and end dates.
        :param start_date: Start date for fetching holidays
        :param end_date: End date for fetching holidays
        :return: List of public holiday dates
        """
        # ---
        year = start_date.year  # Fetch holidays for the year in which end_date falls
        url = f"{self.base_url}/{year}/{self.country_code}"

        print(f"Fetching public holidays from: {url}") 

        response = requests.get(url)
        print(f"Response Status Code: {response.status_code}")  
        print(f"Response Text: {response.text}") 
        if response.status_code != 200:
            raise Exception(f"Failed to fetch holidays: {response.text}")

        holidays = response.json()
        holiday_dates = [datetime.datetime.strptime(holiday["date"], "%Y-%m-%d").date() for holiday in holidays]

        # Filter holidays that fall within the given range
        filtered_holidays = [date for date in holiday_dates if start_date <= date <= end_date]
        print(f"Holidays: {filtered_holidays}")
        return filtered_holidays