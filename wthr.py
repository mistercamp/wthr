from PyQt6.QtWidgets import * 
from PyQt6 import QtCore, QtGui 
from PyQt6.QtGui import * 
from PyQt6.QtCore import * 
from noaa_sdk import NOAA
from datetime import datetime
import threading
import subprocess
import time
import json
import os

stop_event = threading.Event()
pwd =  os.getcwd()

zip_code = '75082'
country = 'US' 


img_map = {'Thunderstorms': {'icon': 'storm_icon.png', 'day': 'storm_bg.png', 'night': 'storm_bg.png'},             
           'Fog': {'icon': 'fog_icon.png', 'day': 'fog_bg.png', 'night': 'fog_bg.png'}, 
           'Snow': {'icon': 'snow_icon.png', 'day': 'snow_day.png', 'night': 'snow_night.png'},
           'rain': {'icon': 'storm_icon.png', 'day': 'rain_day.png', 'night': 'rain_night.png'},
           'drizzle': {'icon': 'storm_icon.png', 'day': 'drizzle_day.png', 'night': 'drizzle_night.png'},
           'frost': {'icon': 'frost_icon.png', 'day': 'frost_day.png', 'night': 'frost_night.png'},
           'Cloudy': {'icon': 'cloudy_icon.png', 'day': 'cloudy_day.png', 'night': 'cloudy_night.png'},
           'Sunny': {'icon': 'sunny_icon.png', 'day': 'sunny_day.png', 'night': 'clear_night.png'},
           'clear': {'icon': 'sunny_icon.png', 'day': 'clear_day.png', 'night': 'clear_night.png'}}

vars_dict = {'day1': {'high': '', 'low': '', 'description': ''}, 
             'day2': {'high': '', 'low': '', 'description': ''}, 
             'day3': {'high': '', 'low': '', 'description': ''}, 
             'day4': {'high': '', 'low': '', 'description': ''}, 
             'day5': {'high': '', 'low': '', 'description': ''}}


def get_json(key):
    with open(pwd + '/settings.json' ,'r+') as file:
        file_data = json.load(file)
        return file_data[key]

def write_json(key, value, cat_flag):
    with open(pwd + '/settings.json' ,'r+') as file:
        file_data = json.load(file)
    if cat_flag == True:
        file_data["categories"][key] = value
    else:
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


class WeatherPanel(QWidget):
    def __init__(self, temp, bg, description):
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

        self.get_forecast()
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
        self.zip_lbl.setText('at ' + zip_code)
        self.zip_lbl.setStyleSheet("color: white")
        self.zip_lbl.setFont(QFont('Arial', 12))
        self.zip_lbl.resize(200, 100)
        self.zip_lbl.move(55, 40)
        
        i = 1
        x_pos, y_pos = 50, 150
        for key in vars_dict:        
            vars_dict[key]['description'] =  QLabel(self)            
            pixmap = QPixmap(pwd + get_img('icon', self.description[i])).scaled(75, 75, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.FastTransformation)
            vars_dict[key]['description'].setPixmap(pixmap)
            vars_dict[key]['description'].resize(pixmap.width(), pixmap.height())
            vars_dict[key]['description'].move(x_pos, y_pos + 40)  
        
            vars_dict[key]['low'] =  QLabel(self)
            vars_dict[key]['low'].setText('Low:   ' + str(round(((9/5) * self.low_temps[i]['value']) + 32)) + u"\u00b0" + 'F')
            vars_dict[key]['low'].setStyleSheet("color: white")
            vars_dict[key]['low'].setFont(QFont('Arial', 12))
            vars_dict[key]['low'].resize(200, 100)
            vars_dict[key]['low'].move(x_pos, y_pos + 100) 
            
            vars_dict[key]['high'] =  QLabel(self)
            vars_dict[key]['high'].setText('High:  ' + str(round(((9/5) * self.high_temps[i]['value']) + 32)) + u"\u00b0" + 'F')
            vars_dict[key]['high'].setStyleSheet("color: white")
            vars_dict[key]['high'].setFont(QFont('Arial', 12))
            vars_dict[key]['high'].resize(200, 100)
            vars_dict[key]['high'].move(x_pos, y_pos + 125)  
            
            #print(self.day[i] + ':', self.description[i])
            x_pos += 100
            i += 1

    def get_forecast(self):
        self.forecast_exp = NOAA().get_forecasts(zip_code, country, type='forecastGridData')
        self.high_temps = self.forecast_exp['maxTemperature']['values']
        self.low_temps = self.forecast_exp['minTemperature']['values']        
        
        self.forecast = NOAA().get_forecasts('75044', 'US', type='forecast')
        self.description = {}
        self.day = {}
        dict_idx = 1
        wxr_idx = 1
        while wxr_idx < len(self.forecast):
            self.description[dict_idx] = self.forecast[wxr_idx]['shortForecast']
            self.day[dict_idx] = self.forecast[wxr_idx]['name']
            if not 'night' in self.forecast[wxr_idx]['name'].lower():
                dict_idx += 1                
            wxr_idx += 1
        
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
    def __init__(self): 
        super().__init__() 
        
        self.get_current()
        self.make_icon()
  
        ############### Menu Config ###############        
        self.icon = QIcon(pwd + "/img/temp/icon.png")
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        
        self.icon2 = QIcon(pwd + get_img('icon', self.curr_type))
        self.tray2 = QSystemTrayIcon()
        self.tray2.setIcon(self.icon2)
        self.tray2.setVisible(True)

        self.menu = QMenu()

        ################ More Menu ################    
        self.more = QAction("More")
        self.more.triggered.connect(self.open_panel)
        self.menu.addAction(self.more)                    
     
        ################ Quit Menu ################
        self.quit = QAction("Quit")
        self.quit.triggered.connect(app.quit)
        self.menu.addAction(self.quit)

        ############### System Tray ###############
        self.tray.setContextMenu(self.menu)
        self.tray2.setContextMenu(self.menu)
        self.start_timer(1800)
        
    def open_panel(self):
        self.panel_w = WeatherPanel(self.curr_temp, get_img('bg', self.curr_type), self.curr_type)
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
        t = 0
        while t < 3:
            try:
                self.current_data = list(NOAA().get_observations(zip_code, country))
                break
            except:
                t += 1
                time.sleep(300)
        self.curr_temp = round(((9/5) * self.current_data[0]['temperature']['value']) + 32)
        self.curr_type = self.current_data[0]['textDescription']
        #print('Current:', self.curr_temp, self.curr_type)

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
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    gui = GUI()
    app.exec()
