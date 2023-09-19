import os
from qgis.PyQt.QtWidgets import QAction, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox


# update button
def _edit_layer(self):
    selectedIndex = self.selected_rows_indexes[0]
    user_layer = self.user_layers[selectedIndex]
    lid = user_layer["id"]
    url_edit_layer = '/api/user_layers/' + lid + "/"

    req_body = {}

    if self.dlg_edit_layer.checkBox_update_meta.isChecked():
        # update meta
        layer_name = self.dlg_edit_layer.text_name.toPlainText()

        if len(layer_name) > 0:
            layer_description = self.dlg_edit_layer.text_description.toPlainText()
            layer_tags_plain = self.dlg_edit_layer.text_tags.toPlainText()
            layer_tags = layer_tags_plain.split(",")
            layer_tags_string = ""
            for lt in layer_tags:
                if lt != "":
                    layer_tags_string += '"' + lt + '"' + ","
            layer_tags_string = layer_tags_string[:0] + "[" + layer_tags_string[0:-1] + "]"

            req_body["title"] = layer_name
            req_body["tag"] = layer_tags_string
            req_body["description"] = layer_description
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Необходимо заполнить название слоя")
            msg.setWindowTitle("Статус")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()

    if self.dlg_edit_layer.checkBox_update_geom.isChecked():
        # update geometry
        if self.dlg_edit_layer.map_layers_cb.currentLayer() != None:
            isSelected = self.dlg_edit_layer.checkBox_selected.isChecked()
            layer_to_add = self.dlg_edit_layer.map_layers_cb.currentLayer()
            if layer_to_add.type().name == "Raster":
                # upload raster
                self.layerCopyPath_add = layer_to_add.dataProvider().dataSourceUri()
                data_type = "raster"
            else:
                # create geopackage
                self._create_gpkg_from_layer(layer_to_add, isSelected)
                data_type = "gpkg"

            req_body["data_type"] = data_type
            req_body["options"] = '{}'
            req_body["file"] = (os.path.basename(self.layerCopyPath_add), open(self.layerCopyPath_add, 'rb'),
                             'application/octet-stream')
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Для обновления геометрии необходимо выбрать слой")
            msg.setWindowTitle("Ошибка обновления слоя")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()

    # try to update layer
    try:
        req_edit_layers = self.api.patch(url_edit_layer, data=req_body)
        if req_edit_layers["id"]:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Слой успешно обновлён")
            msg.setWindowTitle("Статус")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()
            self.dlg_edit_layer.close()
            self._refresh_click()
            self.dlg_layers.raise_()
            self.dlg_layers.activateWindow()
    except Exception as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(str(e))
        msg.setWindowTitle("Ошибка обновления слоя")
        msg.setStandardButtons(QMessageBox.Ok)
        returnValue = msg.exec()
    self._clear_folder(self.folderCopyPath_add)


# edit layer button
def _edit_click(self):
    self.dlg_edit_layer.show()
    selectedIndex = self.selected_rows_indexes[0]
    user_layer = self.user_layers[selectedIndex]
    self.dlg_edit_layer.text_name.setText(user_layer["title"])
    self.dlg_edit_layer.text_description.setText(user_layer["description"])
    self.dlg_edit_layer.text_tags.setText(",".join(user_layer["tag"]))

    try:
        self.dlg_edit_layer.map_layers_cb.currentIndexChanged['QString'].disconnect(self._is_raster_lyr_edit)
        self.dlg_edit_layer.checkBox_update_geom.stateChanged.disconnect(self._edit_geom)
        self.dlg_edit_layer.checkBox_update_meta.stateChanged.disconnect(self._edit_meta)
        self.dlg_edit_layer.edit_layer_button.clicked.disconnect(self._edit_layer)
    except TypeError:
        pass
    self.dlg_edit_layer.map_layers_cb.currentIndexChanged['QString'].connect(self._is_raster_lyr_edit)
    self.dlg_edit_layer.checkBox_update_geom.stateChanged.connect(self._edit_geom)
    self.dlg_edit_layer.checkBox_update_meta.stateChanged.connect(self._edit_meta)
    self.dlg_edit_layer.edit_layer_button.clicked.connect(self._edit_layer)