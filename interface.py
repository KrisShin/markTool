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
)
from PyQt6.QtGui import QAction
from pathlib import Path
import sys
from PyQt6.QtCore import Qt, QAbstractTableModel
import typing
import pandas as pd


from settings import (
    TABLE_FILE_COLUMN_SPAN,
    TABLE_FILE_ROW_SPAN,
    TABLE_RULE_COLUMN_SPAN,
    TABLE_RULE_ROW_SPAN,
    WINDOW_POSITION,
    WINDOW_SIZE,
    WINDOW_TITLE,
)


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])


class InterfaceMianWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_widget()
        self._set_widget()
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
        self.button_edit_rule = QPushButton('edit rule')
        self.button_delete_rule = QPushButton('delete rule')
        self.button_generate_QR_code = QPushButton('generate QRCard')
        self.button_trigger_server = QPushButton('start server')
        self.button_refresh_score = QPushButton('refresh score')
        self.button_export_data = QPushButton('export csv')

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
        # self.button_add_rule.clicked.connect(
        #     self.table_rule.rowsInserted(QModelIndex, 1, 2)
        # )
        self.button_edit_rule.setCheckable(True)
        self.button_delete_rule.setCheckable(True)
        self.button_generate_QR_code.setCheckable(True)
        self.button_trigger_server.setCheckable(True)
        self.button_refresh_score.setCheckable(True)
        # self.button_export_data.setCheckable(True)
        self.button_export_data.clicked.connect(self.init_data)

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
            self.table_rule, 10, 0, TABLE_RULE_ROW_SPAN, TABLE_RULE_COLUMN_SPAN
        )
        grid.addWidget(
            self.check_exclude_edge_score, TABLE_FILE_ROW_SPAN, TABLE_RULE_COLUMN_SPAN
        )
        grid.addWidget(
            self.label_exclude_edge_score,
            TABLE_FILE_ROW_SPAN,
            TABLE_RULE_COLUMN_SPAN + 1,
        )
        grid.addWidget(
            self.button_add_rule, TABLE_FILE_ROW_SPAN + 1, TABLE_RULE_COLUMN_SPAN, 1, 2
        )
        grid.addWidget(
            self.button_edit_rule, TABLE_FILE_ROW_SPAN + 2, TABLE_RULE_COLUMN_SPAN, 1, 2
        )
        grid.addWidget(
            self.button_delete_rule,
            TABLE_FILE_ROW_SPAN + 3,
            TABLE_RULE_COLUMN_SPAN,
            1,
            2,
        )
        grid.addWidget(
            self.line_edit_max_score, TABLE_FILE_ROW_SPAN, TABLE_RULE_COLUMN_SPAN + 2
        )
        grid.addWidget(
            self.line_edit_min_score,
            TABLE_FILE_ROW_SPAN + 1,
            TABLE_RULE_COLUMN_SPAN + 2,
        )
        grid.addWidget(
            self.line_edit_score_step,
            TABLE_FILE_ROW_SPAN + 2,
            TABLE_RULE_COLUMN_SPAN + 2,
        )
        grid.addWidget(
            self.button_generate_QR_code,
            TABLE_FILE_ROW_SPAN,
            TABLE_RULE_COLUMN_SPAN + 3,
        )
        grid.addWidget(
            self.button_trigger_server,
            TABLE_FILE_ROW_SPAN + 1,
            TABLE_RULE_COLUMN_SPAN + 3,
        )
        grid.addWidget(
            self.button_refresh_score,
            TABLE_FILE_ROW_SPAN + 2,
            TABLE_RULE_COLUMN_SPAN + 3,
        )
        grid.addWidget(
            self.button_export_data, TABLE_FILE_ROW_SPAN + 3, TABLE_RULE_COLUMN_SPAN + 3
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
            self.textEdit_files.setText('\n'.join(files[0]))

    def init_data(self):
        data = pd.DataFrame(
            [],
            columns=['file name', 'score', 'like', 'total'],
        )
        self.table_file_model = TableModel(data)
        self.table_file.setModel(self.table_file_model)
        data = pd.DataFrame(
            [],
            columns=['rule', 'weight'],
        )
        self.table_rule_model = TableModel(data)
        self.table_rule.setModel(self.table_rule_model)
        self.statusBar().showMessage('Ready')

    def trigger_server(self):
        button_text = self.button_trigger_server.text()
        print(f'Server status {button_text}')
        if button_text == 'start server':
            self.button_trigger_server.setText('stop server')
        else:
            self.button_trigger_server.setText('start server')

    def add_rule(self):
        # self.table_rule_model
        ...


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InterfaceMianWindow()
    ex.show()
    sys.exit(app.exec())
