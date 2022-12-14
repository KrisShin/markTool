import os
from PyQt6.QtCore import Qt, QAbstractTableModel
import pandas as pd
from src.settings import (
    EDITABLE,
    RULES,
    WORKS,
    TABLE_FILE_DEFAULT_HEADER,
    TABLE_FILE_HEADER,
    TABLE_RULE_HEADER,
)
from src.utils import save_file


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

    def _validate_rule_name(self, value, index):
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
        return old_rule

    def setData(self, index, value, role):
        if EDITABLE == False:
            return EDITABLE
        header_text = self._data.columns[index.column()]
        if role == Qt.ItemDataRole.EditRole and self._validate_edit(header_text, value):
            global WORKS, RULES
            if header_text == TABLE_RULE_HEADER[0]:
                old_rule = self._validate_rule_name(value, index)
                if old_rule is False:
                    return False
                RULES[value] = RULES.pop(old_rule)
                TABLE_FILE_HEADER.insert(-1, value)
                self._main_window.table_file_model.layoutChanged.emit()
                self._main_window.table_rule_model.layoutChanged.emit()

            elif header_text == TABLE_RULE_HEADER[1]:
                # validate all weights sum over 1 or not
                value = float(value)
                sum_rule_weight = sum(RULES.values())
                if sum_rule_weight > 1 or sum_rule_weight + value > 1:
                    self._main_window.show_prompt(
                        'Total weight of rule can not over 1.'
                    )
                    return False
                RULES[self._data.loc[index.row()][0]] = value
            elif header_text not in TABLE_FILE_DEFAULT_HEADER:
                try:
                    path = self._data.loc[index.row()][0]
                except KeyError:
                    return False
                WORKS[os.path.split(path)[-1]][header_text] = float(value)
            else:
                return False
            save_file({'WORKS': WORKS})
            save_file({'RULES': RULES})
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

    def concat(self, rows_df):
        self._data = pd.concat((self._data, rows_df), ignore_index=True)

    def drop(self, labels, axis=0):
        self._data.drop(labels=labels, axis=axis, inplace=True)

    def query_index(self, header, value):
        sub_df = self._data.query(
            f'''{header} == {value if isinstance(value, int|float) else f'"{value}"'}'''
        )
        if sub_df.shape[0] > 1:
            self._main_window.statusBar().showMessage(
                f'Search {value} from {header} error.'
            )
            return
        return sub_df.index
