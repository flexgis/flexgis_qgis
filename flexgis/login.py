import os
from pathlib import Path
from qgis.PyQt.QtGui import QIcon, QDesktopServices
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import QSize, QUrl
from ..constants import (
    SIGN_UP_URL
)
from ..api import ApiClient

# login button
def _log_in(self):
    """
    Login user
    """
    self.username = self.dlg.username.text()
    self.password = self.dlg.password.text()
    self.domain = self.dlg.domain.text()

    self.api = ApiClient(self.domain)

    try:
        req_auth = self.api.login(self.username, self.password)
        self.dlg.close()
        self.dlg_layers.show()
        self.connect_hyperlinks()
        try:
            self.dlg_layers.button_add.clicked.disconnect(self._add_click)
            self.dlg_layers.button_delete.clicked.disconnect(self._del_click)
            self.dlg_layers.button_edit.clicked.disconnect(self._edit_click)
            self.dlg_layers.button_refresh.clicked.disconnect(self._refresh_click)
            self.dlg_layers.button_logout.clicked.disconnect(self._logout_click)
            self.dlg_layers.layer_table.itemSelectionChanged.disconnect(self._select_table_row)
        except TypeError:
            pass
        self.dlg_layers.username_label.setText(self.username)

        # fill table
        self._create_table()

        # add icons to buttons
        root_path = Path(__file__).parents[1]
        imgPath_add = os.path.join(
            root_path,
                'icons',
                'FQ_add.png',
                )
        print('imgPath_add')
        print(imgPath_add)
        self.dlg_layers.button_add.setIcon(QIcon(imgPath_add))
        self.dlg_layers.button_add.setIconSize(QSize(25, 25))

        imgPath_remove = os.path.join(
            root_path,
                'icons',
                'FQ_remove.png',
                )
        self.dlg_layers.button_delete.setIcon(QIcon(imgPath_remove))
        self.dlg_layers.button_delete.setIconSize(QSize(25, 25))

        imgPath_edit = os.path.join(
            root_path,
                'icons',
                'FQ_edit.png',
                )
        self.dlg_layers.button_edit.setIcon(QIcon(imgPath_edit))
        self.dlg_layers.button_edit.setIconSize(QSize(25, 25))

        imgPath_refresh = os.path.join(
            root_path,
                'icons',
                'FQ_refresh.png',
                )
        self.dlg_layers.button_refresh.setIcon(QIcon(imgPath_refresh))
        self.dlg_layers.button_refresh.setIconSize(QSize(25, 25))

        imgPath_logout = os.path.join(
            root_path,
                'icons',
                'FQ_exit.png',
                )
        self.dlg_layers.button_logout.setIcon(QIcon(imgPath_logout))
        self.dlg_layers.button_logout.setIconSize(QSize(25, 25))

        self.dlg_layers.button_add.clicked.connect(self._add_click)
        self.dlg_layers.button_delete.clicked.connect(self._del_click)
        self.dlg_layers.button_edit.clicked.connect(self._edit_click)
        self.dlg_layers.button_refresh.clicked.connect(self._refresh_click)
        self.dlg_layers.button_logout.clicked.connect(self._logout_click)
        self.dlg_layers.layer_table.itemSelectionChanged.connect(self._select_table_row)

    except Exception as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(str(e))
        msg.setWindowTitle("Ошибка авторизации")
        msg.setStandardButtons(QMessageBox.Ok)
        returnValue = msg.exec()


# logout button
def _logout_click(self):
    """
    Logout user
    """
    print('_logout_click(self)')
    self.connect_hyperlinks()
    try:
        self.dlg.sign_up_button.clicked.disconnect(self._sign_up)
        self.dlg.log_in_button.clicked.disconnect(self._log_in)
    except TypeError:
        pass
    self.dlg.sign_up_button.clicked.connect(self._sign_up)
    self.dlg.log_in_button.clicked.connect(self._log_in)
    # user logout
    self.dlg_layers.close()
    print('self.dlg_layers.close()')
    self.dlg.show()


# open sign up page
def _sign_up(self):
    """
    Open browser with sign up
    """
    QDesktopServices.openUrl(QUrl(SIGN_UP_URL))

