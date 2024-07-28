# TE_scraper
Python code to scrape data from Trading Economics website

Allows selection of macroeconomic indicator categories and publication date range for scraping. 
The current version scrapes data for all available countries.

## Config Schema

Top level keys:

- parameters: `list[str]`
    - list of sets of the following parameters:
        - start_date: `str`
            - the first day of the first month in the date range
        - end_date: `str`
            - the first day of the last month in the date range, i.e. if end_date is equal to 1.12.2023 then the data will also be scraped for the whole of December
        - category: `str`
            - category name - must be checked in the page source code, as it does not correspond to the names to be selected in the drop-down category bar

Example config:

```json
{
    "parameters": [
    {
        "start_date": "2022-11-01",
        "end_date": "2023-10-01",
        "category": "inflation"
    },
    {
        "start_date": "2022-11-01",
        "end_date": "2023-10-01",
        "category": "gdp"
    },
    {
        "start_date": "2022-11-01",
        "end_date": "2023-10-01",
        "category": "trade"
    }
    ]
}