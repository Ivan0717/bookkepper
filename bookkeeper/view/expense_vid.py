"""
Widget for expense table
"""
from models.expense import Expense

from repository.sqlite_repository import SQLiteRepository
from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QTableWidget
from typing import Any


class ExpenceWidget(QWidget):
    def __init__(self,data: list[list[Any]],exp_repo: SQLiteRepository[Expense]) -> None:
        super().__init__()
        self.data = data
        self.exp_repo = exp_repo
        layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Последние расходы")
        layout.addWidget(message)

        self.expenses_table = QtWidgets.QTableWidget(4, 20)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        self.expenses_table.setHorizontalHeaderLabels(["Дата", "Сумма", "Категории", "Комментарий"])
        self.col_to_attr = {0: "expense_date", 1: "amount", 2: "category", 3: "comment"}

        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

        self.expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.expenses_table.cellDoubleClicked.connect(self.double_click)
        self.expenses_table.verticalHeader().hide()

        layout.addWidget(self.expenses_table)
        self.setLayout(layout)

    def double_click(self, row: int, column: int) -> None:
        """ Обрабатывает двойное нажатие на ячейку """
        self.expenses_table.cellChanged.connect(self.exp_edit)

    def exp_edit(self, row: int, column: int) -> None:
        """ Обрабатывает изменение ячейки """
        self.expenses_table.cellChanged.disconnect(self.exp_edit)
        pk = int(self.data[row][-1])
        new_val = self.expenses_table.item(row, column).text()
        attr = self.col_to_attr[column]
        self.exp_repo.update_attr(pk, attr, new_val)



        