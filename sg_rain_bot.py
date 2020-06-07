import time
import logging
from sg_rain_bot.bot import Bot
from sg_rain_bot.db import DataBase
from sg_rain_bot.raindata import RainData
from telegram.error import NetworkError, Unauthorized

api_token = '' #enter your api token
n = 3 #bot will check for rain every n minutes

#check weather every n minutes and send to suscribers if rain
def send_updates_to_suscribers(bot, db, rain_data, last_time, n):
    '''Every n minutes, check for rain and send to all suscribers
    Args:
        bot: Bot object
        db: DataBase object
        rain_data: RainData object
        last_time (float): output of time.time()
        n (int): Interval between checks in minutes
    Returns:
        last_time (float): output of time.time()
    '''
    if not last_time or time.time() > last_time + n*60:
        logger.debug(f'Checking for rain... ({time.time()} > {last_time} + {n}*60)')
        last_time = time.time()
        text = rain_data.get_text()
        logger.debug(f'Rain report: {text}')
        ls_tup = db.get_ls_rows()
        ls_ids = [x[0] for x in ls_tup]
        if text:
            for id in ls_ids:
                bot.send_text(id, text, delete_last=1)
    return last_time

#add suscriber for any message received
def handle_updates(bot, db):
    '''Gets updates from bot and replies the users with the same text they sent.'''
    ls_updates = bot.get_updates()
    for tup in ls_updates:
        id, text = tup
        add_id_to_db(id, db)
        bot.send_text(id, f'{id} added to suscriber list!\nYou will get a notification when there is rain in SG.')

#core
def main():
    global api_token
    db_init_string = 'CREATE TABLE IF NOT EXISTS users(id INTEGER)'
    db = DataBase(db_init_string)
    if not api_token: api_token = get_api_token()
    bot = Bot(api_token)
    rain_data = RainData()
    last_time = None
    while 1:
        try:
            last_time = send_updates_to_suscribers(bot, db, rain_data, last_time, n)
            handle_updates(bot, db)
        except NetworkError:
            time.sleep(1)
        except Unauthorized:
            update_id += 1
        except Exception as e:
            logger.error(f'Exception {str(e)}')
            time.sleep(1)

def add_id_to_db(id, db):
    '''Adds id to db if it is new
    Args:
        id (int) - telegram id of user
        db (DataBase) - DataBase object
    '''
    ls_rows = db.get_ls_rows()
    if id not in [x[0] for x in ls_rows]:
        db.insert_id(id)
        logger.info(f'New user {id} added.')

def get_api_token():
    try:
        with open ('api_token.txt', 'r') as f:
            api_token = f.readline()
        return api_token
    except:
        assert api_token, 'Whoops! Please provide an api_token.'

if __name__ == '__main__':
    #logging
    logger = logging.getLogger('sg_rain_bot')
    logger.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler() #stream log
    c_handler.setLevel(logging.DEBUG) #DEBUG INFO ERROR
    c_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(c_handler)
    f_handler = logging.FileHandler('log.log') #file log
    f_handler.setLevel(logging.ERROR)
    f_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [%(module)s]: %(message)s'))
    logger.addHandler(f_handler)
    #main
    main()