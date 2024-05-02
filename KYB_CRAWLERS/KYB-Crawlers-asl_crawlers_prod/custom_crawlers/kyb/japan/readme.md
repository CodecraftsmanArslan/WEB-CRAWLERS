# Crawler: Japan

## Crawler Introduction
This Python script is a web scraper designed to extract information from the [National Tax Agency (NTA)](https://www.houjin-bangou.nta.go.jp/kensaku-kekka.html). The script use selenium to crawl to data page using postcodes, get HTML, use beautifulsoup to parse, and inserts relevant information into a PosgreSQL data table named "tranlate_reports."

## Data Structure
The extracted data is structured into a dictionary containing various key-value pairs. The script defines functions such as `prepare_data` and `prapare_obj` to structure and prepare data for insertion into a database.

### Sample Data Structure
```json
"data": {
  "name": "Ｏｎ－Ｐｒｅｍ株式会社",
  "meta_detail": {
    "aliases": "オンプレム",
    "update_date": "令和2年6月18日"
  },
  "country_name": "Japan",
  "crawler_name": "custom_crawlers.kyb.japan.test2.py",
  "addresses_detail": [
    {
      "type": "general_address",
      "address": "東京都中央区日本橋本町３丁目３番６号ワカ末ビル７階"
    }
  ],
  "additional_detail": [
    {
      "data": [
        {
          "date": "令和2年6月15日",
          "old_name": "アンスクランブル  Ｕｎｓｃｒａｍｂｌｅ株式会社",
          "reason_for_change": "商号又は名称の変更"
        },
        {
          "date": "平成30年9月5日",
          "old_name": "Ｕｎｓｃｒａｍｂｌｅ合同会社",
          "reason_for_change": "商号又は名称の変更"
        }
      ],
      "type": "change_history_information"
    }
  ],
  "registration_date": "平成27年10月5日",
  "registration_number": "8010003017405"
}
```

## Crawler Type
This is a web scraper crawler that uses the `selenium` library crawl to data page, get HTML data and then use `beautifulsoup` to parse and extract required information.
## Additional Dependencies
- `selenium`
- `beautifulsoup4`

## Estimated Processing Time
The processing time for the crawler is estimated > one month.

## How to Run the Crawler
1. Set up a virtual environment if necessary.
2. Set the necessary environment variables in a `.env` file.
3. Install the required dependencies: `pip install -r requirements.txt`
4. Install the custom service dependency in dist directory: `pip install custom_crawler-1.0.tar.gz` 
5. Run the script: `python3 custom_crawlers/kyb/japan/japan.py`