import os
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsMapLayerProxyModel

# upload layer button
def _add_layer(self):
    layer_name = self.dlg_add_layer.text_name.toPlainText()
    if len(layer_name) > 0:
        layer_description = self.dlg_add_layer.text_description.toPlainText()
        layer_tags_plain = self.dlg_add_layer.text_tags.toPlainText()
        layer_tags = layer_tags_plain.split(",")
        layer_tags_string = ""
        for lt in layer_tags:
            if lt != "":
                layer_tags_string += '"' + lt + '"' + ","

        layer_tags_string = layer_tags_string[:0] + "[" + layer_tags_string[0:-1] + "]"

        isSelected = self.dlg_add_layer.checkBox_selected.isChecked()
        layer_to_add = self.dlg_add_layer.map_layers_cb.currentLayer()

        if layer_to_add.type().name == "Raster":
            # upload raster
            self.layerCopyPath_add = layer_to_add.dataProvider().dataSourceUri()
            data_type = "raster"
        else:
            # create geopackage
            self._create_gpkg_from_layer(layer_to_add, isSelected)
            data_type = "gpkg"

        if os.path.isfile(self.layerCopyPath_add):
            url_add_layer = '/api/load/user_data/'
            req_body = {
                "title": layer_name,
                "tag": layer_tags_string,
                "description": layer_description,
                "data_type": data_type,
                "options": '{}',
                "file": (os.path.basename(self.layerCopyPath_add), open(self.layerCopyPath_add, 'rb'), 'application/octet-stream')
            }
            print(req_body)

        try:
            req_add_layers = self.api.create_layer(req_body)
            if req_add_layers["code"] == 200:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Слой успешно добавлен")
                msg.setWindowTitle("Статус")
                msg.setStandardButtons(QMessageBox.Ok)
                returnValue = msg.exec()
                self.dlg_add_layer.close()
                self._refresh_click()
                self.dlg_layers.raise_()
                self.dlg_layers.activateWindow()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(str(e))
            msg.setWindowTitle("Ошибка загрузки слоя")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()

        self._clear_folder(self.folderCopyPath_add)
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Необходимо заполнить название слоя")
        msg.setWindowTitle("Статус")
        msg.setStandardButtons(QMessageBox.Ok)
        returnValue = msg.exec()

# add layer button
def _add_click(self):
    self.dlg_add_layer.show()
    if self.dlg_add_layer.map_layers_cb.currentLayer() != None:
        self.dlg_add_layer.add_layer_button.setEnabled(True)
    else:
        self.dlg_add_layer.add_layer_button.setEnabled(False)
    self.dlg_add_layer.map_layers_cb.setFilters(QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer | QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.RasterLayer)
    try:
        self.dlg_add_layer.map_layers_cb.currentIndexChanged['QString'].disconnect(self._is_raster_lyr)
        self.dlg_add_layer.add_layer_button.clicked.disconnect(self._add_layer)
    except TypeError:
        pass
    self.dlg_add_layer.map_layers_cb.currentIndexChanged['QString'].connect(self._is_raster_lyr)
    self.dlg_add_layer.add_layer_button.clicked.connect(self._add_layer)

