from collections import defaultdict
import os
from threading import Thread
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
import pandas as pd
from src.data_model import TableModel
from src.functions import export_csv, generate_qr_code, get_total_score
from src.utils import read_file, save_file
from src.server_apis import WebServerManager


from src.settings import (
    EDITABLE,
    RULES,
    WORKS,
    SERVER_ALLOWED,
    TABLE_FILE_COLUMN_SPAN,
    TABLE_FILE_HEADER,
    TABLE_FILE_ROW_SPAN,
    TABLE_RULE_COLUMN_SPAN,
    TABLE_RULE_HEADER,
    TABLE_RULE_ROW_SPAN,
    WINDOW_POSITION,
    WINDOW_SIZE,
    WINDOW_TITLE,
    SERVER_THREAD,
)


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
        self.button_confirm = QPushButton('confirm')
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

        self._enabled_widget = [
            self.table_file,
            self.table_rule,
            self.check_exclude_edge_score,
            # self.label_exclude_edge_score,
            self.line_edit_max_score,
            self.line_edit_min_score,
            self.line_edit_score_step,
            # self.button_confirm,
            self.button_add_rule,
            self.button_delete_rule,
        ]

    def _set_widget(self):
        self.action_open_files = QAction('choose files', self)
        self.action_open_files.setShortcut('Ctrl+O')
        self.action_open_files.triggered.connect(self.showDialog)

        # self.table_rule.setHorizontalHeader(QHeaderView(['a', 'b']))

        self.button_trigger_server.setCheckable(True)
        self.button_trigger_server.clicked[bool].connect(self.trigger_server)

        self.button_add_rule.clicked.connect(self.add_rule)
        self.button_delete_rule.clicked.connect(self.delete_rule)
        self.button_confirm.setCheckable(True)
        self.button_confirm.clicked[bool].connect(self.confirm_config)
        self.button_generate_qr_code.clicked.connect(self.generate_qr_code)
        self.button_trigger_server.clicked.connect(self.trigger_server)
        self.button_refresh_score.clicked.connect(self.refresh_score)
        self.button_export_data.clicked.connect(self.export_csv)

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
            self.button_confirm,
            TABLE_FILE_ROW_SPAN + 4,
            TABLE_RULE_COLUMN_SPAN + 1,
            1,
            2,
        )
        grid.addWidget(
            self.button_trigger_server,
            TABLE_FILE_ROW_SPAN,
            TABLE_RULE_COLUMN_SPAN + 4,
            1,
            2,
        )
        grid.addWidget(
            self.button_generate_qr_code,
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
        if not EDITABLE:
            self.show_prompt('Release widget first.')
            return False
        home_dir = str(Path.home())
        files = QFileDialog.getOpenFileNames(self, 'open uri', home_dir)

        if files[0]:
            WORKS.clear()
            row_count = len(files[0])
            rule_df = {rule: [0] * row_count for rule in RULES}
            rows_df = pd.DataFrame(
                {
                    'file name': files[0],
                    'score': [0] * row_count,
                    **rule_df,
                    'total': [0] * row_count,
                }
            )
            self.init_table_file_data()
            self.table_file_model.concat(rows_df)
            WORKS.update({os.path.split(path)[-1]: {'uri': path} for path in files[0]})
            save_file({'WORKS': WORKS})
            self.table_file_model.layoutChanged.emit()
        self.statusBar().showMessage('Select files done')

    def _init_data(self):
        self.init_table_file_data()
        self.init_table_rule_data()
        self.statusBar().showMessage('Ready')

    def init_table_file_data(self):
        data = pd.DataFrame(
            list(),
            columns=TABLE_FILE_HEADER,
        )
        self.table_file_model = TableModel(data, self)
        self.table_file.setModel(self.table_file_model)

    def init_table_rule_data(self):
        data = pd.DataFrame(
            list(),
            columns=TABLE_RULE_HEADER,
        )
        self.table_rule_model = TableModel(data, self)
        self.table_rule.setModel(self.table_rule_model)

    def show_prompt(self, text):
        self.message_box.setText(text)
        self.message_box.exec()

    def trigger_server(self):
        global SERVER_THREAD, SERVER_ALLOWED
        if not self.button_confirm.isChecked():
            self.show_prompt('Please confirm first.')
            self.button_trigger_server.setChecked(False)
            return
        if self.button_trigger_server.isChecked():
            if not SERVER_THREAD:
                SERVER_THREAD = Thread(target=WebServerManager.launch_server)
                SERVER_THREAD.start()
                SERVER_ALLOWED = True
                self.show_prompt('server started')
            self.button_trigger_server.setText('stop server')
            self.statusBar().showMessage(f'Server status launched')
        else:
            if SERVER_THREAD:
                SERVER_ALLOWED = False
                SERVER_THREAD = None
                self.show_prompt('server stop')
            self.statusBar().showMessage(f'Server status stoped')
            self.button_trigger_server.setText('start server')
        save_file({'SERVER_ALLOWED': SERVER_ALLOWED})

    def add_rule(self):
        if '' in RULES:
            self.show_prompt('Please input name of rule first.')
            return
        RULES[''] = 0
        rows_df = pd.DataFrame({'rule': [''], 'weight': [0]})
        self.table_rule_model.concat(rows_df)
        self.table_rule_model.layoutChanged.emit()
        self.statusBar().showMessage('add rule')
        save_file({'RULES': RULES})

    def delete_rule(self):
        index = self.table_rule_model.index(self.table_rule.currentIndex().row(), 0)
        try:
            value = self.table_rule_model.itemData(index)[0]
        except KeyError:
            return
        df_index = self.table_rule_model.query_index(TABLE_RULE_HEADER[0], value)
        self.table_rule_model.drop(df_index)
        TABLE_FILE_HEADER.pop(TABLE_FILE_HEADER.index(value))
        self.table_file_model.drop(value, axis=1)
        RULES.pop(value)
        self.table_rule_model.layoutChanged.emit()
        self.table_file_model.layoutChanged.emit()
        self.statusBar().showMessage('delete rule')
        save_file({'RULES': RULES, 'TABLE_FILE_HEADER': TABLE_FILE_HEADER})

    def _validate_score_range_step(
        self, value_max_score, value_min_score, value_score_step
    ):
        try:
            value_max_score = round(float(value_max_score), 2)
        except ValueError:
            return False, 'max score error'
        try:
            value_min_score = round(float(value_min_score), 2)
        except ValueError:
            return False, 'min score error'
        try:
            value_score_step = round(float(value_score_step), 2)
        except ValueError:
            return False, 'score step error'

        if not all((value_max_score > 0, value_min_score >= 0, value_score_step > 0)):
            return False, 'must more than 0'

        if value_min_score > value_max_score:
            return False, 'min score greater than max score'

        if (value_max_score - value_min_score) / value_score_step % 1 != 0:
            return False, 'step error'
        return True, None

    def _set_widget_enabled(self, widgets: list | None = None):
        if widgets is None:
            widgets = self._enabled_widget
        for widget in widgets:
            widget.setEnabled(EDITABLE)

    def confirm_config(self):
        global EDITABLE, SERVER_ALLOWED
        if self.button_confirm.isChecked():
            value_max_score = self.line_edit_max_score.text()
            value_min_score = self.line_edit_min_score.text()
            value_score_step = self.line_edit_score_step.text()
            is_valid, error = self._validate_score_range_step(
                value_max_score, value_min_score, value_score_step
            )
            if not is_valid:
                self.show_prompt(error)
                self.button_confirm.setChecked(False)
                return
            self.button_confirm.setText('release')
            EDITABLE = False
            SERVER_ALLOWED = False
        else:
            EDITABLE = True
            SERVER_ALLOWED = True
            value_max_score = None
            value_min_score = None
            value_score_step = None
            self.button_confirm.setText('confirm')

        self._set_widget_enabled()
        save_file(
            {
                'EDITABLE': EDITABLE,
                'SERVER_ALLOWED': SERVER_ALLOWED,
                'value_max_score': value_max_score,
                'value_min_score': value_min_score,
                'value_score_step': value_score_step,
            }
        )

    def _refresh_file_table_data(self):
        data = []
        for work in WORKS.values():
            line = [work['uri'], work.get('score', 0)]
            for header in RULES:
                line.append(work.get(header, 0))
            line.append(work.get('total', 0))
            data.append(line)
        df = pd.DataFrame(data, columns=TABLE_FILE_HEADER)
        self.init_table_file_data()
        self.table_file_model.concat(df)
        self.table_file_model.layoutChanged.emit()

    def refresh_score(self):
        global RULES, WORKS
        if not self.button_confirm.isChecked():
            self.show_prompt('Please confirm first.')
            self.button_trigger_server.setChecked(False)
            return
        WORKS = read_file('WORKS')
        exclude_edge = self.check_exclude_edge_score.isChecked()
        score_weight = 1 - sum(RULES.values())
        rule_total_mapping = defaultdict(lambda: 0)
        for work in WORKS.values():
            for key in RULES:
                rule_total_mapping[key] += work.get(key, 0)

        for work in WORKS.values():
            scores = work.get('scores')
            if not scores:
                continue
            scores = list(scores.values())
            if exclude_edge:
                scores.pop(scores.index(max(scores)))
                scores.pop(scores.index(min(scores)))
            work['score'] = sum(scores) / len(scores)
            work['total'] = round(
                get_total_score(work['score'], score_weight, work, rule_total_mapping),
                3,
            )
        self._refresh_file_table_data()
        self.statusBar().showMessage(read_file('status_msg'))

    def generate_qr_code(self):
        if generate_qr_code():
            self.show_prompt('Success')
            return
        self.show_prompt('Error')

    def export_csv(self):
        if export_csv():
            self.show_prompt('Sucess')
            return
        self.show_prompt('Error')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InterfaceMianWindow()
    ex.show()
    sys.exit(app.exec())
