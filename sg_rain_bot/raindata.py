import logging
import bs4 as bs
import urllib.request

logger = logging.getLogger('sg_rain_bot.raindata')

# Pardon the spaghetti code. This class was written a long time ago, haven't gotten around to refactor it yet.
class RainData:
    def __init__(self):
        '''Initilizes Bot object with attributes:
            previous_text (str): previously generated rain report text
            first_time (int): 1 if raindata is new, 0 if generated raindata before        
        '''
        self.previous_text = ''
        self.first_time = 1
        logger.info('RainData loaded!')
        
    def get_text(self):
        '''
        Returns:
            rain_report_str (str): Formatted rain report text to send to telegram users
            is_new_info (int): 1 if is new info, 0 o.w.
        '''
        source = urllib.request.urlopen('http://www.weather.gov.sg/weather-forecast-2hrnowcast-2/').read()
        soup = bs.BeautifulSoup(source,'html.parser')

        timing = soup.find('span', {'class':'time'}).text
        tables = soup.find_all('table')
        report = ''
        rain_list = []
        for table in tables:
            table_rows = table.find_all('tr')
            for tr in table_rows:
                td = tr.find_all('td')
                row = [i.text for i in td]
                if row:
                    weather = row[1][1:]
                    weather_wordlist = weather.split()
                    for word in weather_wordlist:
                        if word.lower() in rain_words:
                            rain_list.append((region_dict[row[0]], row[0], row[1][1:], region_index.index(region_dict[row[0]])))
        if rain_list:
            i=0
            j=0
            while i < 3:
                j=0
                while j < 3:
                    marked = 0
                    for tuple in rain_list:
                        if region_grid[i][j] == tuple[0]:
                            report += '{} '.format(tuple[0])
                            marked = 1
                            break
                    j+=1
                    if not marked: report += '__ '
                report += '\n'
                i+=1
            rain_list.sort(key = lambda tuple: tuple[3]) #sort region index
            rain_list.sort(key = lambda tuple: tuple[2]) #sort weather
            weather = ''
            region = ''
            for tuple in rain_list:
                if tuple[2] != weather:
                    weather = tuple[2]
                    region = ''
                    report += '\n<b>{}</b>'.format(weather.title())
                if tuple[0] != region:
                    region = tuple[0]
                    report += '\n- [{}] '.format(region)
                report += '{}, '.format(tuple[1])
            rain_report_str = f'<b>Latest Forecast {timing}:</b>\n{report}\nwww.weather.gov.sg/weather-rain-area-50km'
        else:
            rain_report_str = 'No rain warnings :)'
            if self.first_time:
                self.first_time = 0
                self.previous_text = rain_report_str        
        if self.previous_text == rain_report_str:
            is_new_info = 0
        else:
            self.previous_text = rain_report_str
            is_new_info = 1
        return rain_report_str, is_new_info
                
rain_words = ['rain', 'showers']
region_index = ['NW','NN','NE','WW','CC','EE','SW','SS','SE']
region_grid = [['NW', 'NN', 'NE'], ['WW', 'CC', 'EE'], ['SW', 'SS', 'SE']]
region_dict = {
'Ang Mo Kio' : 'CC'
,'Bedok' : 'SE'
,'Bishan' : 'CC'
,'Boon Lay' : 'SW'
,'Bukit Batok' : 'WW'
,'Bukit Merah' : 'SS'
,'Bukit Panjang' : 'CC'
,'Bukit Timah' : 'CC'
,'Central Water Catchment' : 'CC'
,'Changi' : 'EE'
,'Choa Chu Kang' : 'WW'
,'Clementi' : 'WW'
,'City' : 'SS'
,'Geylang' : 'SE'
,'Hougang' : 'EE'
,'Jalan Bahar' : 'WW'
,'Jurong East' : 'WW'
,'Jurong Island' : 'SW'
,'Jurong West' : 'WW'
,'Kallang' : 'SE'
,'Lim Chu Kang' : 'NW'
,'Mandai' : 'NN'
,'Marine Parade' : 'SE'
,'Novena' : 'CC'
,'Pasir Ris' : 'EE'
,'Paya Lebar' : 'EE'
,'Pioneer' : 'SW'
,'Pulau Tekong' : 'EE'
,'Pulau Ubin' : 'NE'
,'Punggol' : 'NE'
,'Queenstown' : 'SS'
,'Seletar' : 'NE'
,'Sembawang' : 'NN'
,'Sengkang' : 'NE'
,'Sentosa' : 'SS'
,'Serangoon' : 'CC'
,'Southern Islands' : 'SS'
,'Sungei Kadut' : 'NW'
,'Tampines' : 'EE'
,'Tanglin' : 'CC'
,'Tengah' : 'WW'
,'Toa Payoh' : 'CC'
,'Tuas' : 'SW'
,'Western Islands' : 'SW'
,'Western Water Catchment' : 'NW'
,'Woodlands' : 'NN'
,'Yishun' : 'NN'
}