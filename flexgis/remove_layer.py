from qgis.PyQt.QtWidgets import QMessageBox

# delete layer button
def _del_click(self):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setText("Вы уверены, что хотите удалить выбранные слои из источников данных FlexGIS?")
    msg.setWindowTitle("Удаление слоев")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    returnValue = msg.exec()
    if returnValue == QMessageBox.Ok:
        layers_ids = []
        for ri in self.selected_rows_indexes:
            for ul in self.user_layers:
                if ul["qgis_table_index"] == ri:
                    layers_ids.append(ul["id"])
        for lyr_id in layers_ids:
            self._delete_layers(lyr_id)
        self._refresh_click()

# remove layer
def _delete_layers(self, lid: str):
    url_del_layers = '/api/user_layers/' + lid
    try:
        del_response = self.api.delete(url_del_layers)
    except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(str(e))
            msg.setWindowTitle("Ошибка удаления слоя")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()