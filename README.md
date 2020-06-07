# SG Rain Bot
## Project Summary
* Weather data is web-scraped from a government weather website ([See webscraping notebook!](https://github.com/MichaelOw/SG_Rain_Bot/blob/master/notebooks/web_scraping.ipynb))
* Rain alerts are sent to users through a Telegram bot

## Run it yourself!

### Step 1: Load Telegram API Token
Create a bot and get the API token: https://core.telegram.org/bots#6-botfather

Open sg_rain_bot.py and edit line below.

    api_token = '' #enter your api token

### Step 2: Run the Python script
    $ python sg_rain_bot.py

### Step 3: Start getting alerts
Add the bot to your Telegram app and start receiving rain alerts!

![alt text](demo.png)
