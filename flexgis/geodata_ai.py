from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QLineEdit, QPushButton
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsPointXY
from qgis.gui import *
from qgis.PyQt.QtCore import QVariant
import requests 
import webbrowser
            
def _ai_layer(self):
    st = self.dlg_ai.request.toPlainText()
    if len(st) > 0: 
        username = self.username
        password = self.password
        endpoint = '/auth/token/login' 
        data = {'username': username, 'password': password}
        response = self.api.post(endpoint, data = data)
        self.token = response.get('auth_token')   
        
        # check tarif
        headers = {"Authorization": f"Token {self.token}"}
        response = requests.get('https://gis.flexatel.xyz/auth/users/me/', headers = headers)
        if "billing_plan" in response.json().keys():
            tarif = response.json()['billing_plan']
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Geodata AI доступен только для онлайн-пользователей с тарифом Pro.<br>Пожалуйста, смените тариф <a href="https://gis.flexatel.xyz/tariffs">https://gis.flexatel.xyz/tariffs</a>')
            msg.setWindowTitle("Plan restriction")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()
            return
        
        if tarif != 'Pro':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Geodata AI доступен только для пользователей с тарифом Pro.<br>Пожалуйста, смените тариф <a href="https://gis.flexatel.xyz/tariffs">https://gis.flexatel.xyz/tariffs</a>')
            msg.setWindowTitle("Plan restriction")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()
            return
                
        headers = {
                "Referer": "https://gis.flexatel.xyz/builder/",
                "Authorization": f"Token {self.token}",
                "Accept": "application/json"}
        url = "https://srv.flexatel.xyz/query"
        params = {"q": st}
        response = requests.get(url, params = params, headers = headers)
        geojson_data = response.json()
        try:
            k = list(geojson_data.keys())[0]
            print(response.json())
            print(response.text)
            if response.status_code == 200 and k:
                geom_type = geojson_data[k][0]['geometry']['type']
                lyr = QgsVectorLayer(f'{geom_type}?crs=epsg:4326', st, 'memory')
                field_names = list(geojson_data[k][0]['properties'].keys())
                fields = []
                for field_name in field_names:
                    fields.append(QgsField(field_name, QVariant.String))
                lyr.dataProvider().addAttributes(fields)
                lyr.updateFields()

                def create_geometry(geom_type, coordinates):
                    if geom_type == 'Point':
                        return QgsGeometry.fromPointXY(QgsPointXY(coordinates[0], coordinates[1]))
                    if geom_type == 'MultiPoint':
                        return QgsGeometry.fromPointXY(QgsPointXY(coordinates[0][0], coordinates[0][1]))
                    elif geom_type == 'LineString':
                        return QgsGeometry.fromPolylineXY([QgsPointXY(coord[0], coord[1]) for coord in coordinates])
                    elif geom_type == 'MultiLineString':
                        return QgsGeometry.fromPolylineXY([QgsPointXY(coord[0], coord[1]) for coord in coordinates[0]])
                    elif geom_type == 'Polygon':
                        return QgsGeometry.fromPolygonXY([[QgsPointXY(coord[0], coord[1]) for coord in coordinates[0]]])
                    elif geom_type == 'MultiPolygon':
                        return QgsGeometry.fromPolygonXY([[QgsPointXY(coord[0], coord[1]) for coord in coordinates[0][0]]])
                
                features = []
                for feature in geojson_data[k]:
                    properties = feature['properties']
                    geom_type = feature['geometry']['type']
                    coordinates = feature['geometry']['coordinates']
                    geom = create_geometry(geom_type, coordinates)
                    new_feature = QgsFeature()
                    new_feature.setGeometry(geom)
                    new_feature.setAttributes(list(properties.values()))
                    features.append(new_feature)
                lyr.dataProvider().addFeatures(features)
                QgsProject.instance().addMapLayer(lyr)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Слой успешно загружен")
                msg.setWindowTitle("Статус")
                msg.setStandardButtons(QMessageBox.Ok)
                returnValue = msg.exec()
                
                self.dlg_ai.request.clear()
                
            else:
                print("error", response.status_code, response.text)
                
        except IndexError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Не удалось выполнить запрос")
            msg.setWindowTitle("Ошибка")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()
            print(response.json())
            print(response.text)
            
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Не удалось выполнить запрос")
            msg.setWindowTitle("Ошибка")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()
            print(response.json())
            print(response.text)

    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Заполните поле запроса")
        msg.setWindowTitle("Ошибка")
        msg.setStandardButtons(QMessageBox.Ok)
        returnValue = msg.exec()

def _ai_inf(self):
    url = 'https://flexgis.ru/instructions#widgets-geodata-ai'
    webbrowser.open(url)
    
def _ai_click(self):  
    self.dlg_ai.show()
    try:
        self.dlg_ai.inf_button.clicked.disconnect(self._ai_inf)
    except TypeError:
        pass 
    self.dlg_ai.inf_button.clicked.connect(self._ai_inf)
    text = self.dlg_ai.request
    try:
        self.dlg_ai.search_button.setEnabled(False)
        self.dlg_ai.search_button.clicked.disconnect(self._ai_layer)   
    except TypeError:
        pass
    if text != None:
        self.dlg_ai.search_button.setEnabled(True)
        self.dlg_ai.search_button.clicked.connect(self._ai_layer)