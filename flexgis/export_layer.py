from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsPointXY
from qgis.gui import *
from qgis.PyQt.QtCore import QVariant
import requests

def _export_layer(self): 
    selectedIndex = self.selected_rows_indexes[0]
    user_layer = self.user_layers[selectedIndex]
    username = self.username
    password = self.password
    endpoint = '/auth/token/login' 
    data = {'username': username, 'password': password}
    response = self.api.post(endpoint, data = data)
    self.token = response.get('auth_token')    
    url = "https://gis.flexatel.xyz/geoserver/user_data/ows"
    headers = {
            "Referer": "https://gis.flexatel.xyz/builder/",
            "Authorization": f"Token {self.token}"}

    if user_layer['type'] != 'raster':
        params = {
            "srsName": "EPSG:4326",
            "cql_filter": "1=1",
            "propertyNames": "",
            "format_options": "charset=UTF-8",
            "request": "GetFeature",
            "service": "WFS",
            "typeName": "user_data:" + user_layer['name'],
            "version": "2.0.0",
            "settings": "",
            "outputFormat": "application/json"
        }

        response = requests.get(url, params = params, headers = headers) 
        if response.status_code == 200:
            geojson_data = response.json()
            print(geojson_data)
            geom_type = user_layer['geometryType'].lstrip('org.locationtech.jts.geom.')
            lyr = QgsVectorLayer(f'{geom_type}?crs=epsg:4326', str(user_layer['title']), 'memory')
            field_names = list(geojson_data['features'][0]['properties'].keys())
            fields = []
            for field_name in field_names:
                fields.append(QgsField(field_name, QVariant.String))
            lyr.dataProvider().addAttributes(fields)
            lyr.updateFields()

            def create_geometry(geom_type, coordinates):
                if geom_type == 'Point':
                    return QgsGeometry.fromPointXY(QgsPointXY(coordinates[0], coordinates[1]))
                
                elif geom_type == 'MultiPoint':
                    points = [QgsPointXY(coord[0], coord[1]) for coord in coordinates]
                    return QgsGeometry.fromMultiPointXY(points)
                
                elif geom_type == 'LineString':
                    points = [QgsPointXY(coord[0], coord[1]) for coord in coordinates]
                    return QgsGeometry.fromPolylineXY(points)
                
                elif geom_type == 'MultiLineString':
                    lines = []
                    for line in coordinates:
                        points = [QgsPointXY(coord[0], coord[1]) for coord in line]
                        lines.append(points)
                    return QgsGeometry.fromMultiPolylineXY(lines)
                
                elif geom_type == 'Polygon':
                    rings = []
                    for ring in coordinates:
                        points = [QgsPointXY(coord[0], coord[1]) for coord in ring]
                        rings.append(points)
                    return QgsGeometry.fromPolygonXY(rings)
                
                elif geom_type == 'MultiPolygon':
                    polygons = []
                    for polygon in coordinates:
                        rings = []
                        for ring in polygon:
                            points = [QgsPointXY(coord[0], coord[1]) for coord in ring]
                            rings.append(points)
                        polygons.append(rings)
                    return QgsGeometry.fromMultiPolygonXY(polygons)
                
                else:
                    print(f"Unknown geometry type: {geom_type}")
                    return None
                
            def validate_and_fix_geometry(geom, geom_type):
                if not geom:
                    return None
                
                if geom.isGeosValid():
                    return geom
                                
                try:
                    fixed_geom = geom.makeValid()
                    if fixed_geom:
                        original_wkt = geom.wkt()
                        fixed_wkt = fixed_geom.wkt()
                        
                        if original_wkt.split(' ')[0] == fixed_wkt.split(' ')[0]:
                            return fixed_geom
                        else:
                            print(f"Geometry type changed from {geom.wktType()} to {fixed_geom.wktType()}")
                            return geom
                    
                    return geom 
                        
                except Exception as e:
                    print(f"Error fixing geometry: {e}")
                    return geom 
                return None

            features = []
            valid_count = 0
            invalid_count = 0
            
            for feature in geojson_data['features']:
                properties = feature['properties']
                geom_type = feature['geometry']['type']
                coordinates = feature['geometry']['coordinates']
                geom = create_geometry(geom_type, coordinates)
                
                if geom:
                    valid_geom = validate_and_fix_geometry(geom, geom_type)
                else:
                    valid_geom = geom
                
                if valid_geom:
                    new_feature = QgsFeature()
                    new_feature.setGeometry(valid_geom)
                    new_feature.setAttributes(list(properties.values()))
                    features.append(new_feature)
                    valid_count += 1
                else:
                    print(f"Error with creation geometry: {geom_type}")
                    invalid_count += 1

            if features:
                lyr.dataProvider().addFeatures(features)
                QgsProject.instance().addMapLayer(lyr)

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Слой успешно загружен")
                msg.setWindowTitle("Статус")
                msg.setStandardButtons(QMessageBox.Ok)
                returnValue = msg.exec()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("В слое нет подходящих объектов")
                msg.setWindowTitle("Ошибка")
                msg.setStandardButtons(QMessageBox.Ok)
                returnValue = msg.exec()
            
        else:
            print("error", response.status_code, response.text)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(response.text)
            msg.setWindowTitle("Layer loading error")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()
    
    else: # for raster 
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Попытка загрузки растрового слоя")
            msg.setWindowTitle("Ошибка")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()


def _export_click(self):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setText("Вы уверены, что хотите загрузить слой из FlexGIS?")
    msg.setWindowTitle("Сохранение слоя")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    returnValue = msg.exec()
    if returnValue == QMessageBox.Ok:
        _export_layer(self)