import logging
import bs4 as bs
import urllib.request

logger = logging.getLogger('sg_rain_bot.raindata')

class RainData:
    def __init__(self):
        '''Initilizes Bot object with attributes:
            prev_report (str): previously generated rain report text   
        '''
        self.prev_report = ''
        logger.info('RainData loaded!')
        
    def get_text(self):
        '''
        Returns:
            report (str): Formatted rain report text to send to telegram users
            is_new_info (int): 1 if is new info, 0 o.w.
        '''
        # webscraping
        source = urllib.request.urlopen('http://www.weather.gov.sg/weather-forecast-2hrnowcast-2/').read()
        soup = bs.BeautifulSoup(source,'html.parser')
        ls_town = []
        ls_weather = []
        forecast_period = soup.find('span', {'class':'time'}).text

        # get towns and weather
        for table in soup.find_all('table'):
            for tr in table.find_all('tr'):
                ls_td = tr.find_all('td')
                if ls_td:
                    town = ls_td[0].text
                    weather = ls_td[1].text.replace('\xa0', '')
                    ls_town.append(town)
                    ls_weather.append(weather)

        # get rain levels
        ls_rain_level = []
        for weather in [x.lower() for x in ls_weather]:
            rain_level = 0
            if 'rain' in weather or 'shower' in weather:
                if 'light' in weather:
                    rain_level = -1
                elif 'thunder' in weather:
                    rain_level = -3
                else:
                    rain_level = -2
            ls_rain_level.append(rain_level)
            
        # get other data structures
        ls_region = [dt_town_region.get(town, 'unknown') for town in ls_town]
        dt_region_max_rain_level = {region:1 for region in dt_region_town}
        for region, rain_level in zip(ls_region, ls_rain_level):
            if region=='unknown': continue
            if rain_level<dt_region_max_rain_level[region]:
                dt_region_max_rain_level[region] = rain_level
        #ls_region_order = [dt_region_order.get(region, 9) for region in ls_region]
        #ls_report = list(zip(ls_rain_level, ls_weather, ls_region_order, ls_region, ls_town))
        ls_report = list(zip(ls_rain_level, ls_weather, ls_town))

        # generate report string part 1
        report = ''
        weather_c = None
        region_c = None
        town_c = None
        no_rain = 1
        for rain_level, weather, town in sorted(ls_report):
            if rain_level>=0:
                continue #skip non rain
            else:
                no_rain = 0
            if weather_c != weather:
                weather_c = weather
                report += f'\n<b>{dt_rain_level_emoji[rain_level]} {weather.title()}</b>\n'
            if town_c != town:
                town_c = town
                report += f'<i>{town}, </i>'

        # generate report string part 2
        if no_rain:
            report+='No rain warnings :)'
            
        # generate report string part 3
        report += f'\n\n<b>Forecast Period:</b> {forecast_period}'
        for i, (_, rain_level) in enumerate(dt_region_max_rain_level.items()):
            if i%3==0:
                report+='\n'
            report+=dt_rain_level_emoji[rain_level]
            
        report+=f'\n<i>Map Summary</i>\n[<a href="{ls_links[0]}">2 Hour Forecast</a>] [<a href="{ls_links[1]}">Live Rain Radar</a>]'
        # generate is_new_info
        is_new_info = 1
        if self.prev_report == '' and no_rain: #first time and no rain
            is_new_info = 0
        #elif self.prev_report == report: #same report as previous
            #is_new_info = 0
        self.prev_report = report
        return report, is_new_info

ls_links = [
    #'http://www.weather.gov.sg/weather-forecast-2hrnowcast-2/',
    #'http://www.weather.gov.sg/weather-rain-area-50km',
    'https://www.nea.gov.sg/weather#weather-forecast2hr',
    'https://www.nea.gov.sg/weather/rain-areas',
]

dt_rain_level_emoji = {
    0:'\u2600',         #sun
    -1:'\u2601',        #cloud
    -2:'\U0001F327',    #cloud with rain
    -3:'\u26C8',        #cloud with rain and thunder
}
dt_region_town = {
'NW': ['Lim Chu Kang',
    'Sungei Kadut',
    'Western Water Catchment'],
'NN': ['Mandai', 
    'Sembawang',
    'Woodlands', 
    'Yishun'],
'NE': ['Pulau Ubin',
    'Punggol', 
    'Seletar', 
    'Sengkang'],
'WW': ['Bukit Batok',
    'Choa Chu Kang',
    'Clementi',
    'Jalan Bahar',
    'Jurong East',
    'Jurong West',
    'Tengah'],
'CC': ['Ang Mo Kio',
    'Bishan',
    'Bukit Panjang',
    'Bukit Timah',
    'Central Water Catchment',
    'Novena',
    'Serangoon',
    'Tanglin',
    'Toa Payoh'],
'EE': ['Changi',
    'Hougang',
    'Pasir Ris',
    'Paya Lebar',
    'Pulau Tekong',
    'Tampines'],
'SW': ['Boon Lay', 
    'Jurong Island', 
    'Pioneer', 
    'Tuas',
    'Western Islands'],
'SS': ['Bukit Merah',
    'City', 
    'Queenstown',
    'Sentosa',
    'Southern Islands'],
'SE': ['Bedok',
    'Geylang',
    'Kallang',
    'Marine Parade'],
}
# dt_region_order = {}
# for i, region in enumerate(dt_region_town):
    # dt_region_order[region] = i
dt_town_region = {}
for k, v in dt_region_town.items():
    for town in v:
        dt_town_region[town]=k