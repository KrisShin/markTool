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
    QHeaderView,
    QAbstractItemView,
)
from PyQt6.QtGui import QAction
from pathlib import Path
import sys
from PyQt6.QtCore import Qt, QAbstractTableModel


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
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def load(self):
        print(self._data)
        self.endResetModel()

    def flags(self, index):  # 必须实现的接口方法，不实现，则View中数据不可编辑
        if index.isValid():
            return Qt.ItemFlag.ItemIsEnabled
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    # def headerData(self, section, orientation, role=Qt.DisplayRole):
    #     # 实现标题行的定义
    #     if role != Qt.DisplayRole:
    #         return None

    #     if orientation == Qt.Horizontal:
    #         return self.headers[section]
    #     return int(section + 1)

    # # 以下为编辑功能所必须实现的方法
    # def setData(self, index, value, role=Qt.EditRole):
    #     # 编辑后更新模型中的数据 View中编辑后，View会调用这个方法修改Model中的数据
    #     if index.isValid() and 0 >= index.row() > len(self.datas) and value:
    #         col = index.column()
    #         print(col)
    #         if 0 > col > len(self.headers):
    #             self.beginResetModel()
    #             # if CONVERTS_FUNS[col]:                                         # 必要的时候执行数据类型的转换
    #             #     self.datas[index.row()][col] = CONVERTS_FUNS[col](value)
    #             # else:
    #             #     self.datas[index.row()][col] = value
    #             self.dirty = True
    #             self.endResetModel()
    #             return True
    #     return False

    # def insertRows(self, position, rows=1, index=QModelIndex()):
    #     # position 插入位置；rows 插入行数
    #     self.beginInsertRows(QModelIndex(), position, position + rows - 1)
    #     pass  #  对self.datas进行操作
    #     self.endInsertRows()
    #     self.dirty = True
    #     return True

    # def removeRows(self, position, rows=1, index=QModelIndex):
    #     # position 删除位置；rows 删除行数
    #     self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
    #     pass  #  对self.datas进行操作
    #     self.endRemoveRows()
    #     self.dirty = True
    #     return True


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
        self.botton_add_rule = QPushButton('add rule')
        self.botton_edit_rule = QPushButton('edit rule')
        self.botton_delete_rule = QPushButton('delete rule')
        self.botton_generate_QR_code = QPushButton('generate QRCard')
        self.botton_trigger_server = QPushButton('start server')
        self.botton_refresh_score = QPushButton('refresh score')
        self.botton_export_data = QPushButton('export csv')

        # line edit placeholder
        self.line_edit_max_score.setPlaceholderText('max score')
        self.line_edit_min_score.setPlaceholderText('min score')
        self.line_edit_score_step.setPlaceholderText('score step')

    def _set_widget(self):
        self.action_open_files = QAction('choose files', self)
        self.action_open_files.setShortcut('Ctrl+O')
        self.action_open_files.triggered.connect(self.showDialog)

        self.table_rule.setHorizontalHeader(QHeaderView(['a', 'b']))

        self.botton_trigger_server.setCheckable(True)
        # self.botton_trigger_server.clicked[bool].connect(self.demo_data)
        # self.botton_add_rule.clicked.connect(
        #     self.table_rule.rowsInserted(QModelIndex, 1, 2)
        # )
        self.botton_edit_rule.setCheckable(True)
        self.botton_delete_rule.setCheckable(True)
        self.botton_generate_QR_code.setCheckable(True)
        self.botton_trigger_server.setCheckable(True)
        self.botton_refresh_score.setCheckable(True)
        # self.botton_export_data.setCheckable(True)
        self.botton_export_data.clicked.connect(self.demo_data)

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
            self.botton_add_rule, TABLE_FILE_ROW_SPAN + 1, TABLE_RULE_COLUMN_SPAN, 1, 2
        )
        grid.addWidget(
            self.botton_edit_rule, TABLE_FILE_ROW_SPAN + 2, TABLE_RULE_COLUMN_SPAN, 1, 2
        )
        grid.addWidget(
            self.botton_delete_rule,
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
            self.botton_generate_QR_code,
            TABLE_FILE_ROW_SPAN,
            TABLE_RULE_COLUMN_SPAN + 3,
        )
        grid.addWidget(
            self.botton_trigger_server,
            TABLE_FILE_ROW_SPAN + 1,
            TABLE_RULE_COLUMN_SPAN + 3,
        )
        grid.addWidget(
            self.botton_refresh_score,
            TABLE_FILE_ROW_SPAN + 2,
            TABLE_RULE_COLUMN_SPAN + 3,
        )
        grid.addWidget(
            self.botton_export_data, TABLE_FILE_ROW_SPAN + 3, TABLE_RULE_COLUMN_SPAN + 3
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

    def demo_data(self):
        data = [
            ['file name', 'score', 'like', 'total'],
            [1, 0, 3, 0],
            [3, 5, 1, 0],
        ]
        model = TableModel(data)
        self.table_file.setModel(model)
        data = [
            ['rule', 'weight'],
            ['like', 0.3],
        ]
        model = TableModel(data)
        self.table_rule.setModel(model)
        self.statusBar().showMessage('Ready')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InterfaceMianWindow()
    ex.show()
    sys.exit(app.exec())
