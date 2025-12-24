from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsRasterLayer
from qgis.gui import *
from qgis.PyQt.QtCore import QVariant
import requests
import tempfile
import os

def _export_layer(self): 
    selectedIndex = self.selected_rows_indexes[0]
    user_layer = self.user_layers[selectedIndex]
    username = self.username
    password = self.password
    base_domain = self.domain
    base_domain = base_domain.rstrip('/')
    endpoint = '/auth/token/login' 
    data = {'username': username, 'password': password}
    response = self.api.post(endpoint, data = data)
    self.token = response.get('auth_token')    
    url = f"{base_domain}/geoserver/user_data/ows"
    headers = {
            "Referer": f"{base_domain}/builder/",
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
            geom_type = user_layer['geometryType'].lstrip('org.locationtech.jts.geom.')
            lyr = QgsVectorLayer(f'{geom_type}?crs=epsg:4326', str(user_layer['title']), 'memory')    
            sample_props = geojson_data["features"][0]["properties"]
            fields = []
            def guess_qvariant_type(value):
                if isinstance(value, int):
                    return QVariant.Int
                if isinstance(value, float):
                    return QVariant.Double
                if isinstance(value, str):
                    dt = QtCore.QDateTime.fromString(value, QtCore.Qt.ISODate)
                    if dt.isValid():
                        return QVariant.DateTime
                    return QVariant.String
                return QVariant.String
            for field_name, value in sample_props.items():
                qtype = guess_qvariant_type(value)
                fields.append(QgsField(field_name, qtype))
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
                    attr_values = []
                    for field_name, value in properties.items():
                        if isinstance(value, str):
                            dt = QtCore.QDateTime.fromString(value, QtCore.Qt.ISODate)
                            if dt.isValid():
                                attr_values.append(dt)
                                continue
                        attr_values.append(value)

                    new_feature.setAttributes(attr_values)
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
                msg.setText("Layer was loaded successfully")
                msg.setWindowTitle("Status")
                msg.setStandardButtons(QMessageBox.Ok)
                returnValue = msg.exec()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Layer loading error")
                msg.setWindowTitle("Error")
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
        try:
            temp_dir = tempfile.gettempdir()
            raster_filename = f"{user_layer['name']}.tif"
            raster_path = os.path.join(temp_dir, raster_filename)
            
            wcs_url = f"{base_domain}/geoserver/wcs"
            coverage_name = f"user_rasters:{user_layer['name']}"
                        
            try:
                describe_params = {
                    "service": "WCS",
                    "version": "2.0.1",
                    "request": "DescribeCoverage",
                    "coverageId": coverage_name
                }
                
                describe_response = requests.get(wcs_url, params=describe_params, headers=headers)                
                if describe_response.status_code == 200:
                    get_coverage_params = {
                        "service": "WCS",
                        "version": "2.0.1",
                        "request": "GetCoverage",
                        "coverageId": coverage_name,
                        "format": "image/tiff"
                    }
                    
                    response = requests.get(wcs_url, params=get_coverage_params, headers=headers, stream=True, timeout=30)
                    if response.status_code == 200:
                        with open(raster_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        print(f"raster path: {raster_path}")
                        
                        layer_name = str(user_layer['title'])
                        raster_layer = QgsRasterLayer(raster_path, layer_name)
                        
                        if raster_layer.isValid():
                            QgsProject.instance().addMapLayer(raster_layer)
                            
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Information)
                            msg.setText("Слой успешно загружен")
                            msg.setWindowTitle("Статус")
                            msg.setStandardButtons(QMessageBox.Ok)
                            returnValue = msg.exec()
                        else:
                            raise Exception("Invalid raster layer file")
                    else:
                        raise Exception(f"WCS GetCoverage failed: {response.status_code}")
                else:
                    raise Exception(f"Coverage not found with WCS 2.0.1")
                        
            except Exception as e:
                print(f"Raster download error: {str(e)}")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(f"Ошибка при загрузке растрового слоя: {str(e)}")
                msg.setWindowTitle("Ошибка")
                msg.setStandardButtons(QMessageBox.Ok)
                returnValue = msg.exec()
        except Exception as e:
            print(f"Raster download error: {str(e)}")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"Ошибка при загрузке растрового слоя: {str(e)}")
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