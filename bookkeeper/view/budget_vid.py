"""
Widget of budget table
"""
from models.budget import Budget
from repository.sqlite_repository import SQLiteRepository
from PySide6 import QtWidgets
from PySide6.QtWidgets import (QWidget, QTableWidget)
from typing import Any
from PySide6.QtCore import Qt

def set_data(table: QTableWidget, spent: list[float], day_budget: float) -> None:
    budget = [day_budget, day_budget * 7, day_budget * 30]
    for i, [lost, limit] in enumerate(zip(spent, budget)):
        table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(lost)))
        table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(limit)))


class BudgetWidget(QWidget):
    def __init__(self,budget_repo: SQLiteRepository[Budget]) -> None:
        super().__init__()
        self.budget_repo = budget_repo
        layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Бюджет")
        layout.addWidget(message)
        self.data = self.budgets_to_data()
        spent = [s.sum for s in self.budget_repo.get_all()]

        self.expenses_table = QtWidgets.QTableWidget(2, 3)
        self.expenses_table.setColumnCount(2)
        self.expenses_table.setRowCount(3)
        self.expenses_table.setHorizontalHeaderLabels(["Сумма ","Бюджет "])
        self.expenses_table.setVerticalHeaderLabels(["День ","Неделя ","Месяц "])
        self.row_to_period = {0: "day", 1: "week", 2: "month"}
        horizontalHeader = self.expenses_table.horizontalHeader()
        verticalHeader = self.expenses_table.verticalHeader()

        horizontalHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        horizontalHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        horizontalHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        verticalHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        verticalHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        verticalHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.expenses_table.cellDoubleClicked.connect(self.double_click)
        print(spent)
        set_data(self.expenses_table, spent, self.budget_repo.get(1).budget)

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
        self.budget_repo.update_attr(pk, self.row_to_period[row], new_val)

    def budgets_to_data(self) -> list[list[Any]]:
        """ Конвертирует объекты бюджетов в данные для таблицы """
        data = []
        for period in ["day", "week", "month"]:
            bdgs = [bi for bi in self.budget_repo.get_all() if bi.period == period]
            if len(bdgs) == 0:
                data.append(["- Не установлен -", "", "", None])
            else:
                bdg = bdgs[0]
                item = ([str(bdg.sum),
                         str(bdg.budget),
                         bdg.pk])
                data.append(item)  # type: ignore
        return data
    
    