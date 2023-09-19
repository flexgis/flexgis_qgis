from qgis.PyQt.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView, QAbstractItemView
from qgis.PyQt.QtCore import Qt

# create layer table
def _create_table(self):
    url_layers = '/api/user_layers/'
    try:
        req_layers = self.api.get(url_layers)
        self.user_layers = req_layers
        table = self.dlg_layers.layer_table
        table.setColumnCount(5)
        table.setRowCount(len(self.user_layers))
        table.setHorizontalHeaderLabels(["Название", "Описание", "Тэги", "Объектов", "Тип"])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.user_layers = sorted(self.user_layers, key=lambda d: d['title'].lower())
        for l in range(len(self.user_layers)):
            ul = self.user_layers[l]
            ul["qgis_table_index"] = l
            lyr_tags = ", ".join(ul["tag"])
            lyr_gt = ul["geometryType"].split(".")[-1]
            lyr_fc = QTableWidgetItem(str(ul["feature_count"]))
            lyr_fc.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            table.setItem(l, 0, QTableWidgetItem(ul["title"]))
            table.setItem(l, 1, QTableWidgetItem(ul["description"]))
            table.setItem(l, 2, QTableWidgetItem(lyr_tags))
            table.setItem(l, 3, QTableWidgetItem(lyr_fc))
            table.setItem(l, 4, QTableWidgetItem(lyr_gt))
        table.setAlternatingRowColors(True)
        table.setWordWrap(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    except Exception as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(str(e))
        msg.setWindowTitle("Ошибка получения слоев")
        msg.setStandardButtons(QMessageBox.Ok)
        returnValue = msg.exec()

# select row action
def _select_table_row(self):
    table = self.dlg_layers.layer_table
    items = table.selectedItems()
    rows = {}
    for i in items:
        if i.row() not in rows.keys():
            rows[i.row()] = 1
        else:
            rows[i.row()] += 1

    self.selected_rows_indexes = []
    for r in rows.keys():
        if rows[r] == 5:
            self.selected_rows_indexes.append(r)

    if len(self.selected_rows_indexes) > 0:
        self.dlg_layers.button_delete.setEnabled(True)
        if len(self.selected_rows_indexes) == 1:
            self.dlg_layers.button_edit.setEnabled(True)
        else:
            self.dlg_layers.button_edit.setEnabled(False)
    else:
        self.dlg_layers.button_delete.setEnabled(False)
        self.dlg_layers.button_edit.setEnabled(False)


# refresh layers table
def _refresh_click(self):
    # get layers table
    self._create_table()