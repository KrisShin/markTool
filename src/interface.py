from PyQt6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QApplication,
    QGridLayout,
    QPushButton,
    QTableView,
    QLabel,
    QCheckBox,
    QLineEdit,
    QWidget,
    QMessageBox,
)
from PyQt6.QtGui import QAction
from pathlib import Path
import sys
from PyQt6.QtCore import Qt, QAbstractTableModel
import pandas as pd


from src.settings import (
    EDITABLE,
    RULES,
    TABLE_FILE_COLUMN_SPAN,
    TABLE_FILE_DEFAULT_HEADER,
    TABLE_FILE_HEADER,
    TABLE_FILE_ROW_SPAN,
    TABLE_RULE_COLUMN_SPAN,
    TABLE_RULE_HEADER,
    TABLE_RULE_ROW_SPAN,
    WINDOW_POSITION,
    WINDOW_SIZE,
    WINDOW_TITLE,
)


class TableModel(QAbstractTableModel):
    def __init__(self, data, main_window):
        super(TableModel, self).__init__()
        self._data = data
        self._main_window = main_window

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                value = self._data.iloc[index.row(), index.column()]
                return str(value)

    def setData(self, index, value, role):
        if EDITABLE == False:
            return EDITABLE
        header_text = self._data.columns[index.column()]
        if role == Qt.ItemDataRole.EditRole and self._validate_edit(header_text, value):
            if header_text == TABLE_RULE_HEADER[0]:
                value = str(value).strip()
                if value in RULES:
                    self._main_window.show_prompt(f'{value} already in rules')
                    return False
                try:
                    old_rule = self._data.loc[index.row()][index.column()]
                except KeyError:
                    old_rule = ''
                if old_rule:
                    # rename rule
                    TABLE_FILE_HEADER.pop(TABLE_FILE_HEADER.index(old_rule))
                    self._main_window.table_file_model.rename_header(old_rule, value)
                else:
                    # add rule
                    self._main_window.table_file_model._data.insert(
                        self._main_window.table_file_model.columnCount() - 1, value, 0
                    )
                RULES[value] = RULES.pop(old_rule)
                TABLE_FILE_HEADER.append(value)
                self._main_window.table_file_model.layoutChanged.emit()
                self._main_window.table_rule_model.layoutChanged.emit()

            elif header_text == TABLE_RULE_HEADER[1]:
                # validate all weights sum over 1 or not
                ...
            self._data.iloc[index.row(), index.column()] = value
            return True
        return False

    def headerData(self, col, orientation, role):
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self._data.columns[col]

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

    def rename_header(self, old_name, new_name):
        self._data = self._data.rename(columns={old_name: new_name})

    def _validate_edit(self, header_text, value):
        if header_text == TABLE_RULE_HEADER[0]:
            return bool(str(value).strip())
        if header_text not in TABLE_FILE_DEFAULT_HEADER:
            try:
                f_value = float(value)
                if header_text == TABLE_RULE_HEADER[1] and (f_value > 1 or f_value < 0):
                    self._main_window.show_prompt('Weight must between 0 to 1.')
                    return False
                return True
            except ValueError:
                self._main_window.show_prompt('Please input float.')
                return False
        return False

    def add_rows(self, rows_df):
        self._data = pd.concat((self._data, rows_df), ignore_index=True)

    def del_rows(self):
        ...


class InterfaceMianWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_widget()
        self._set_widget()
        self._init_data()
        self._initUI()

    def _init_widget(self):
        # widgets
        self.table_file = QTableView()
        self.table_rule = QTableView()
        self.check_exclude_edge_score = QCheckBox()
        self.label_exclude_edge_score = QLabel('exclude max/min score')
        self.line_edit_max_score = QLineEdit()
        self.line_edit_min_score = QLineEdit()
        self.line_edit_score_step = QLineEdit()
        self.button_add_rule = QPushButton('add rule')
        self.button_delete_rule = QPushButton('delete rule')
        self.button_generate_qr_code = QPushButton('generate QRCode')
        self.button_trigger_server = QPushButton('start server')
        self.button_refresh_score = QPushButton('refresh score')
        self.button_export_data = QPushButton('export csv')
        self.message_box = QMessageBox(self)

        # line edit placeholder
        self.line_edit_max_score.setPlaceholderText('max score')
        self.line_edit_min_score.setPlaceholderText('min score')
        self.line_edit_score_step.setPlaceholderText('score step')

    def _set_widget(self):
        self.action_open_files = QAction('choose files', self)
        self.action_open_files.setShortcut('Ctrl+O')
        self.action_open_files.triggered.connect(self.showDialog)

        # self.table_rule.setHorizontalHeader(QHeaderView(['a', 'b']))

        self.button_trigger_server.setCheckable(True)
        self.button_trigger_server.clicked[bool].connect(self.trigger_server)

        self.button_add_rule.clicked.connect(self.add_rule)
        # self.button_delete_rule.clicked.connect(self.add_rule)
        # self.button_generate_qr_code.clicked.connect(self.add_rule)
        # self.button_trigger_server.clicked.connect(self.add_rule)
        # self.button_refresh_score.clicked.connect(self.add_rule)
        # self.button_export_data.clicked.connect(self._init_data)

        self.message_box.setWindowTitle("Prompt !!!")
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Files')
        fileMenu.addAction(self.action_open_files)

    def _initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(
            self.table_file, 0, 0, TABLE_FILE_ROW_SPAN, TABLE_FILE_COLUMN_SPAN
        )
        grid.addWidget(
            self.table_rule,
            TABLE_FILE_ROW_SPAN,
            0,
            TABLE_RULE_ROW_SPAN,
            TABLE_RULE_COLUMN_SPAN,
        )
        grid.addWidget(
            self.button_add_rule, TABLE_FILE_ROW_SPAN + TABLE_RULE_ROW_SPAN, 0, 1, 3
        )
        grid.addWidget(
            self.button_delete_rule,
            TABLE_FILE_ROW_SPAN + TABLE_RULE_ROW_SPAN,
            5,
            1,
            3,
        )
        grid.addWidget(
            self.check_exclude_edge_score,
            TABLE_FILE_ROW_SPAN,
            TABLE_RULE_COLUMN_SPAN + 1,
        )
        grid.addWidget(
            self.label_exclude_edge_score,
            TABLE_FILE_ROW_SPAN,
            TABLE_RULE_COLUMN_SPAN + 2,
        )
        grid.addWidget(
            self.line_edit_max_score,
            TABLE_FILE_ROW_SPAN + 1,
            TABLE_RULE_COLUMN_SPAN + 1,
            1,
            2,
        )
        grid.addWidget(
            self.line_edit_min_score,
            TABLE_FILE_ROW_SPAN + 2,
            TABLE_RULE_COLUMN_SPAN + 1,
            1,
            2,
        )
        grid.addWidget(
            self.line_edit_score_step,
            TABLE_FILE_ROW_SPAN + 3,
            TABLE_RULE_COLUMN_SPAN + 1,
            1,
            2,
        )
        grid.addWidget(
            self.button_generate_qr_code,
            TABLE_FILE_ROW_SPAN,
            TABLE_RULE_COLUMN_SPAN + 4,
            1,
            2,
        )
        grid.addWidget(
            self.button_trigger_server,
            TABLE_FILE_ROW_SPAN + 1,
            TABLE_RULE_COLUMN_SPAN + 4,
            1,
            2,
        )
        grid.addWidget(
            self.button_refresh_score,
            TABLE_FILE_ROW_SPAN + 2,
            TABLE_RULE_COLUMN_SPAN + 4,
            1,
            2,
        )
        grid.addWidget(
            self.button_export_data,
            TABLE_FILE_ROW_SPAN + 3,
            TABLE_RULE_COLUMN_SPAN + 4,
            1,
            2,
        )

        widget = QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

        self.setGeometry(*WINDOW_POSITION, *WINDOW_SIZE)
        self.setWindowTitle(WINDOW_TITLE)

    def showDialog(self):
        home_dir = str(Path.home())
        files = QFileDialog.getOpenFileNames(self, 'open uri', home_dir)

        if files[0]:
            rows_df = pd.DataFrame(
                {
                    'file name': files[0],
                    'score': [0] * len(files[0]),
                    'total': [0] * len(files[0]),
                }
            )
            self.table_file_model.add_rows(rows_df)
            self.table_file_model.layoutChanged.emit()

    def _init_data(self):
        data = pd.DataFrame(
            list(),
            columns=TABLE_FILE_HEADER,
        )
        self.table_file_model = TableModel(data, self)
        self.table_file.setModel(self.table_file_model)
        data = pd.DataFrame(
            list(),
            columns=TABLE_RULE_HEADER,
        )
        self.table_rule_model = TableModel(data, self)
        self.table_rule.setModel(self.table_rule_model)
        self.statusBar().showMessage('Ready')

    def show_prompt(self, text):
        self.message_box.setText(text)
        self.message_box.exec()

    def trigger_server(self):
        button_text = self.button_trigger_server.text()
        print(f'Server status {button_text}')
        if button_text == 'start server':
            self.button_trigger_server.setText('stop server')
        else:
            self.button_trigger_server.setText('start server')

    def add_rule(self):
        if '' in RULES:
            self.show_prompt('Please input name of rule first.')
            return
        RULES[''] = 0
        rows_df = pd.DataFrame({'rule': [''], 'weight': [0]})
        self.table_rule_model.add_rows(rows_df)
        self.table_rule_model.layoutChanged.emit()

    def delete_rule(self):
        # rows_df = pd.DataFrame({'rule': [''], 'weight': [0]})
        # self.table_rule_model.add_rows(rows_df)
        # self.table_rule_model.layoutChanged.emit()
        ...


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InterfaceMianWindow()
    ex.show()
    sys.exit(app.exec())
