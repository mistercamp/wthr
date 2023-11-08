from PyQt6.QtWidgets import * 
from PyQt6 import QtCore, QtGui 
from PyQt6.QtGui import * 
from PyQt6.QtCore import * 
from datetime import datetime
import threading
import subprocess
import requests
import pgeocode
import time
import json
import os

stop_event = threading.Event()
pwd =  os.getcwd()

img_map = {'Thunderstorms': {'icon': 'storm_icon.png', 'day': 'storm_bg.png', 'night': 'storm_bg.png'},             
           'Fog': {'icon': 'fog_icon.png', 'day': 'fog_bg.png', 'night': 'fog_bg.png'}, 
           'Snow': {'icon': 'snow_icon.png', 'day': 'snow_day.png', 'night': 'snow_night.png'},
           'rain': {'icon': 'storm_icon.png', 'day': 'rain_day.png', 'night': 'rain_night.png'},
           'drizzle': {'icon': 'storm_icon.png', 'day': 'drizzle_day.png', 'night': 'drizzle_night.png'},
           'frost': {'icon': 'frost_icon.png', 'day': 'frost_day.png', 'night': 'frost_night.png'},
           'Cloudy': {'icon': 'cloudy_icon.png', 'day': 'cloudy_day.png', 'night': 'cloudy_night.png'},
           'Sunny': {'icon': 'sunny_icon.png', 'day': 'sunny_day.png', 'night': 'clear_night.png'},
           'clear': {'icon': 'sunny_icon.png', 'day': 'clear_day.png', 'night': 'clear_night.png'},}

vars_dict = {'day1': {'high': '', 'low': '', 'description': '', 'day': ''}, 
             'day2': {'high': '', 'low': '', 'description': '', 'day': ''}, 
             'day3': {'high': '', 'low': '', 'description': '', 'day': ''}, 
             'day4': {'high': '', 'low': '', 'description': '', 'day': ''}, 
             'day5': {'high': '', 'low': '', 'description': '', 'day': ''}}

def check_config():
    if not os.path.exists(pwd + '/settings.json'):
        with open(pwd + '/settings.json' ,'w') as file:
            tmp = os.path.expanduser("~/")                
            json.dump({"zip_code" : "", "country" : "US", "refresh": "1800", "uri": ""}, file) 
            print("settings.json created")

def get_uri(zipcode, country):
    query = pgeocode.Nominatim(country).query_postal_code(zipcode)
    lon_lat = {"lat": query["latitude"], "lon": query["longitude"]}
    uri = requests.get('https://api.weather.gov/points/' + str(lon_lat['lat']) + ',' + str(lon_lat['lon'])).json()['properties']['forecastGridData']
    return uri

def get_json(key):
    with open(pwd + '/settings.json' ,'r+') as file:
        file_data = json.load(file)
        return file_data[key]

def write_json(key, value):
    with open(pwd + '/settings.json' ,'r+') as file:
        file_data = json.load(file)
    file_data[key] = value
    with open(pwd + '/settings.json' ,'w') as file:
        json.dump(file_data, file) 
   
def get_img(img_type, curr_type):
    #print(img_type, curr_type)
    for i in img_map:
        if i.lower() in curr_type.lower():
            if img_type == 'icon':
                return '/img/icon/' + img_map[i]['icon']
            if img_type == 'bg':
                if datetime.now().hour in range(6, 20):
                    return '/img/bg/' + img_map[i]['day']
                else:
                    return '/img/bg/' + img_map[i]['night']


class SetupPanel(QMainWindow):
    def __init__(self, app):
        super().__init__()
        
        self.app = app
        
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(600, 378)   
        
        bg = QLabel(self)
        pixmap = QPixmap(pwd + '/img/bg/settings.png')
        bg.setPixmap(pixmap)
        bg.resize(600, 378)    
        
        save_btn = QPushButton("Save", self)         
        save_btn.setGeometry(265, 250, 70, 25) 
        save_btn.clicked.connect(self.cancel)
        save_btn.setStyleSheet("border-radius : 50; \
                                background-color : rgba(255, 255, 255, 40); \
                                color: white") 
        
        welcome = QLabel(self)
        welcome.setText("Welcome")
        welcome.setFont(QFont('Arial', 42))
        welcome.setStyleSheet("color: white")
        welcome.setGeometry(182, 60, 250, 75)
        
        welcome2 = QLabel(self)
        welcome2.setText("Please enter your zip code")
        welcome2.setFont(QFont('Arial', 12))
        welcome2.setStyleSheet("color: white")
        welcome2.setGeometry(205, 100, 250, 75)
        
        self.zip_code = QLineEdit(self)
        self.zip_code.setStyleSheet("background-color: rgba(255, 255, 255, 40); \
                                     color: white") 
        self.zip_code.move(200, 175)
        self.zip_code.resize(200, 40)
        self.zip_code.setFocus()
        
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        self.show()   
        
    def cancel(self):
        write_json('zip_code', self.zip_code.text())
        write_json('uri', get_uri(self.zip_code.text(), 'us'))
        self.app.quit()        


class WeatherPanel(QWidget):
    def __init__(self, temp, bg, description, uri):
        super().__init__()
        
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(600, 378)
        self.center()      
        
        self.bg = QLabel(self)
        pixmap = QPixmap(pwd + bg)
        self.bg.setPixmap(pixmap)
        self.bg.resize(600, 378)  
        
        self.close_btn = QLabel(self)
        pixmap = QPixmap(pwd + '/img/icon/close.png')
        self.close_btn.setPixmap(pixmap)
        self.close_btn.move(565, 15)       

        self.get_forecast(uri)
        self.update_weather(temp, description)
        self.oldPos = self.pos()
        
    def update_weather(self, temp, description):
        self.temp_lbl = QLabel(self)         
        self.temp_lbl.setText(str(temp) + u"\u00b0")
        self.temp_lbl.setStyleSheet("color: white")
        self.temp_lbl.setFont(QFont('Arial', 48))
        self.temp_lbl.resize(100, 100)
        self.temp_lbl.move(480, 20)
        
        self.desc_lbl = QLabel(self)
        self.desc_lbl.setText(description)
        self.desc_lbl.setStyleSheet("color: white")
        self.desc_lbl.setFont(QFont('Arial', 32))
        self.desc_lbl.resize(400, 100)
        self.desc_lbl.move(50, 5)
        
        self.zip_lbl = QLabel(self)
        self.zip_lbl.setText('at ' + get_json('zip_code'))
        self.zip_lbl.setStyleSheet("color: white")
        self.zip_lbl.setFont(QFont('Arial', 12))
        self.zip_lbl.resize(200, 100)
        self.zip_lbl.move(55, 40)
        
        i = 0
        x_pos, y_pos = 50, 150
        for key in vars_dict:        
            vars_dict[key]['description'] =  QLabel(self)            
            pixmap = QPixmap(pwd + get_img('icon', self.description[i])).scaled(75, 75, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.FastTransformation)
            vars_dict[key]['description'].setPixmap(pixmap)
            vars_dict[key]['description'].resize(pixmap.width(), pixmap.height())
            vars_dict[key]['description'].move(x_pos, y_pos + 40)  

            vars_dict[key]['day'] =  QLabel(self)
            vars_dict[key]['day'].setText(self.day[i])
            vars_dict[key]['day'].setStyleSheet("color: white")
            vars_dict[key]['day'].setFont(QFont('Arial', 12))
            vars_dict[key]['day'].resize(200, 100)
            vars_dict[key]['day'].move(x_pos + 10, y_pos - 35)
 
            vars_dict[key]['low'] =  QLabel(self)
            vars_dict[key]['low'].setText('Low:   ' + str(self.low_temps[i]) + u"\u00b0" + 'F')
            vars_dict[key]['low'].setStyleSheet("color: white")
            vars_dict[key]['low'].setFont(QFont('Arial', 12))
            vars_dict[key]['low'].resize(200, 100)
            vars_dict[key]['low'].move(x_pos, y_pos + 100) 
            
            vars_dict[key]['high'] =  QLabel(self)
            vars_dict[key]['high'].setText('High:  ' + str(self.high_temps[i]) + u"\u00b0" + 'F')
            vars_dict[key]['high'].setStyleSheet("color: white")
            vars_dict[key]['high'].setFont(QFont('Arial', 12))
            vars_dict[key]['high'].resize(200, 100)
            vars_dict[key]['high'].move(x_pos, y_pos + 125)  
            
            #print(self.day[i] + ':', self.description[i])
            x_pos += 100
            i += 1

    def get_forecast(self, uri):
        self.forecast = requests.get(uri + '/forecast').json()          
        self.high_temps, self.low_temps, self.day, self.description = {}, {}, {}, {}
        wxr_idx, dict_idx = 0, 0
        while wxr_idx < len(self.forecast['properties']['periods']) - 1:
            if 'night' in self.forecast['properties']['periods'][wxr_idx]['name']:
                wxr_idx += 1
            self.high_temps[dict_idx] = self.forecast['properties']['periods'][wxr_idx]['temperature']
            self.low_temps[dict_idx] = self.forecast['properties']['periods'][wxr_idx + 1]['temperature']            
            self.description[dict_idx] = self.forecast['properties']['periods'][wxr_idx]['shortForecast']
            self.day[dict_idx] = self.forecast['properties']['periods'][wxr_idx]['name']               
            wxr_idx += 2
            dict_idx += 1
        
    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()
        if self.mapFromGlobal(QCursor.pos()).x() in range(565, 586) and \
           self.mapFromGlobal(QCursor.pos()).y() in range(15, 36):
               self.hide()

    def mouseMoveEvent(self, event):
        self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos )
        self.dragPos = event.globalPosition().toPoint()
        event.accept()

        
class GUI(QMainWindow):   
    def __init__(self, setup_flag): 
        super().__init__() 
        
        self.zip_code = get_json('zip_code')
        self.country = get_json('country')
        self.uri = get_json('uri')
        
        self.get_current()
        self.make_icon()
        
        self.icon = QIcon(pwd + "/img/temp/icon.png")
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        
        self.icon2 = QIcon(pwd + get_img('icon', self.curr_type))
        self.tray2 = QSystemTrayIcon()
        self.tray2.setIcon(self.icon2)
        self.tray2.setVisible(True)

        self.menu = QMenu()
   
        self.more = QAction("More")
        self.more.triggered.connect(self.open_panel)
        self.menu.addAction(self.more)                    
     
        self.quit = QAction("Quit")
        self.quit.triggered.connect(app.quit)
        self.menu.addAction(self.quit)

        self.tray.setContextMenu(self.menu)
        self.tray2.setContextMenu(self.menu)
        self.start_timer(get_json('refresh'))
        if setup_flag == True:
            self.open_panel()
        
    def open_panel(self):
        self.panel_w = WeatherPanel(self.curr_temp, get_img('bg', self.curr_type), self.curr_type, self.uri)
        #self.panel_w.settings_closed.connect(self.refresh_paths)
        self.panel_w.show()
        
    def start_timer(self, arg):
        bg_t = threading.Thread(target=self.timer_loop, args=(arg, ), daemon=True)
        bg_t.start()
        
    def timer_loop(self, value):
        i = 0
        while True:                               
            while i < int(value): 
                if stop_event.is_set():
                    break       
                time.sleep(1)
                i+=1        
            if stop_event.is_set():
                    break 
            if i == int(value):
                i=0    
            self.update()
    
    def update(self):
        self.get_current()
        self.make_icon()
        self.icon = QIcon(pwd + "/img/temp/icon.png")
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        
        self.icon2 = QIcon(pwd + get_img('icon', self.curr_type))
        self.tray2.setIcon(self.icon2)
        self.tray2.setVisible(True) 
        
    def get_current(self):
        tries, idx = 0, 2 #2 = rockwall
        stop_flag = False
        while not stop_flag:
            try:
                station_list = requests.get(self.uri + '/stations').json()
                station = station_list['features'][idx]['id'] + '/observations'
                self.current_data = requests.get(station).json()['features'][idx]['properties']    
                if self.current_data['temperature']['value'] == None or self.current_data['textDescription'] == None:
                    idx += 1   
                else:
                    break         
            except:
                if tries > 2:
                    stop_flag = True
                tries += 1
                time.sleep(300)
        self.curr_temp = round(1.8 *(self.current_data['temperature']['value']) + 32)
        self.curr_type = self.current_data['textDescription']
        #print('Current:', self.curr_temp, 'Description:', self.curr_type)

    def make_icon(self):
        pic = ''
        for i in range(len(str(self.curr_temp))):
            pic += pwd + '/img/temp/' + str(self.curr_temp)[i] + '.png '
        pic += pwd + '/img/temp/deg.png '    
        img_cmd = 'convert +append ' + pic + '-colorspace RGB ' + pwd + '/img/temp/icon.png'
        try:
            subprocess.run(img_cmd, shell = True, executable="/bin/bash")
        except:
            pass


if __name__ == '__main__':
    print("Starting...")
    while True:
        try:
            check_config()
            setup_flag = False  
            
            if get_json('zip_code') == '':
                setup_flag = True
                setup = QApplication([])
                setup.setQuitOnLastWindowClosed(False)
                setup_w = SetupPanel(setup)
                setup.exec()

            if get_json('uri') == '':
                write_json('uri', get_uri(get_json('zip_code'), get_json('country')))

            app = QApplication([])
            app.setQuitOnLastWindowClosed(False)
            gui = GUI(setup_flag)
            app.exec()
        except:
            print("Restarting...")
            time.sleep(5)