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
)
from PyQt6.QtGui import QAction
from pathlib import Path
import sys
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget

from settings import WINDOW_POSITION, WINDOW_SIZE, WINDOW_TITLE


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


class InterfaceMianWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_widget()
        self.initUI()

    def init_widget(self):
        # widgets
        self.table_file = QTableView()
        self.table_rule = QTableView()
        self.check_exclude_edge_score = QCheckBox()
        self.label_exclude_edge_score = QLabel('去掉最高最低分')
        self.botton_add_rule = QPushButton('添加规则')
        self.botton_edit_rule = QPushButton('编辑规则')
        self.botton_delete_rule = QPushButton('删除规则')
        self.line_edit_max_score = QLineEdit()
        self.line_edit_min_score = QLineEdit()
        self.line_edit_score_step = QLineEdit()
        self.botton_generate_QR_code = QPushButton('生成二维码')
        self.botton_trigger_server = QPushButton('开启服务')
        self.botton_refresh_score = QPushButton('刷新得分')
        self.botton_export_data = QPushButton('导出数据')

        # line edit placeholder
        self.line_edit_max_score.setPlaceholderText('最高打分')
        self.line_edit_min_score.setPlaceholderText('最低打分')
        self.line_edit_score_step.setPlaceholderText('打分间隔')

        # actions
        self.action_open_files = QAction('选择文件夹', self)

    def initUI(self):
        grid = QGridLayout()
        self.demo_data()
        self.setLayout(grid)
        grid.setSpacing(10)
        grid.addWidget(self.table_file, 0, 0, 10, 20)
        grid.addWidget(self.table_rule, 10, 0, 5, 6)
        grid.addWidget(self.check_exclude_edge_score, 10, 6)
        grid.addWidget(self.label_exclude_edge_score, 10, 7)
        grid.addWidget(self.botton_add_rule, 11, 6, 1, 2)
        grid.addWidget(self.botton_edit_rule, 12, 6, 1, 2)
        grid.addWidget(self.botton_delete_rule, 13, 6, 1, 2)
        grid.addWidget(self.line_edit_max_score, 10, 8)
        grid.addWidget(self.line_edit_min_score, 11, 8)
        grid.addWidget(self.line_edit_score_step, 12, 8)
        grid.addWidget(self.botton_generate_QR_code, 10, 9)
        grid.addWidget(self.botton_trigger_server, 11, 9)
        grid.addWidget(self.botton_refresh_score, 12, 9)
        grid.addWidget(self.botton_export_data, 13, 9)

        widget = QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

        self.action_open_files.setShortcut('Ctrl+O')
        self.action_open_files.setStatusTip('选择文件夹')
        self.action_open_files.triggered.connect(self.showDialog)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件')
        fileMenu.addAction(self.action_open_files)

        self.setGeometry(*WINDOW_POSITION, *WINDOW_SIZE)
        self.setWindowTitle(WINDOW_TITLE)

    def showDialog(self):

        home_dir = str(Path.home())
        files = QFileDialog.getOpenFileNames(self, '打开文件路径', home_dir)

        if files[0]:
            self.textEdit_files.setText('\n'.join(files[0]))

    def demo_data(self):
        data = [
            ['文件名', '得分', '点赞量', '总分'],
            [1, 0, 3, 0],
            [3, 5, 1, 0],
        ]
        model = TableModel(data)
        self.table_file.setModel(model)
        data = [
            ['规则', '权重'],
            ['点赞量', 0.3],
        ]
        model = TableModel(data)
        self.table_rule.setModel(model)
        self.statusBar().showMessage('Ready')


def main():
    app = QApplication(sys.argv)
    ex = InterfaceMianWindow()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
