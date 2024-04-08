"""
MainWindow view
"""

from PySide6 import QtWidgets
from PySide6.QtWidgets import (QWidget)

from .expense_vid import ExpenceWidget
from .budget_vid import BudgetWidget
from .edit import EditWidget
from models.category import Category
from models.expense import Expense
from models.budget import Budget
from repository.sqlite_repository import SQLiteRepository
from typing import Any
from datetime import datetime,timedelta
from view.budget_vid import set_data

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,
                category_repo: SQLiteRepository[Category],
                exp_repo: SQLiteRepository[Expense],
                budget_repo: SQLiteRepository[Budget]):
        super().__init__()
        self.setWindowTitle("The Bookkeeper App")
        self.exp_repo = exp_repo
        self.category_repo = category_repo
        self.budget_repo = budget_repo
        layout = QtWidgets.QVBoxLayout()
        self.expence = ExpenceWidget(self.exps_to_data(self.exp_repo.get_all()),self.exp_repo)
        self.budget = BudgetWidget(budget_repo)
        edit_field = EditWidget(self.category_repo,self.exp_repo,self.add_expense)
        
        self.period_to_row= {"day": 0, "week": 1, "month": 2}
        
        self.set_expense_data()
        self.update_spent("day")
        self.update_spent("week")
        self.update_spent("month")

        layout.addWidget(self.expence)
        layout.addWidget(self.budget)
        layout.addWidget(edit_field)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        
    def set_expense_data(self) -> None:
        for i, row in enumerate(self.exps_to_data(self.exp_repo.get_all())):
            for j, x in enumerate(row[:-1]):
                self.expence.expenses_table.setItem(i, j, 
                                                    QtWidgets.QTableWidgetItem(x.capitalize()))


    def catpk_to_name(self, pk: int) -> str:
            """ Возвращает название категории по id (pk) """
            name = [c.name for c in self.category_repo.get_all() if int(c.pk) == int(pk)]
            if len(name):
                return str(name[0])
            return ""

    def exps_to_data(self,exps: list[Expense]) -> list[list[Any]]:
        """ Конвертирует объекты трат в данные для таблицы """
        data = []
        for exp in exps:
            item = ["", "", "", "", exp.pk]
            if exp.expense_date:
                item[0] = str(exp.expense_date)
            if exp.amount:
                item[1] = str(exp.amount)
            if exp.category:
                item[2] = str(
                    self.catpk_to_name(exp.category))
            if exp.comment:
                item[3] = str(exp.comment)
            data.append(item)
        return data

    def add_expense(self,sum_line,cats_box):
        obj = Expense(sum_line,cats_box)
        self.exp_repo.add(obj)
        self.set_expense_data()
        self.update_spent("day")
        self.update_spent("week")
        self.update_spent("month")
        day_limit = self.budget_repo.get(1)
        print([s.sum for s in self.budget_repo.get_all()])
        set_data(self.budget.expenses_table,[s.sum for s in self.budget_repo.get_all()],day_limit.budget)

    def update_spent(self,period:str) -> None:  # type: ignore
        """ Обновляет траты за период бюждетов по заданному репозиторию exp_repo """
        date = datetime.now().isoformat()[:10]  # YYYY-MM-DD format
        if period.lower() == "day":
            date_mask = f"{date}"
            period_exps = self.exp_repo.get_all_like(like={"expense_date": date_mask})
        elif period.lower() == "week":
            weekday_now = datetime.now().weekday()
            day_now = datetime.fromisoformat(date)
            first_week_day = day_now - timedelta(days=weekday_now)
            period_exps = []
            for i in range(7):
                weekday = first_week_day + timedelta(days=i)
                date_mask = f"{weekday.isoformat()[:10]}"
                period_exps += self.exp_repo.get_all_like(like={"expense_date": date_mask})
        elif period.lower() == "month":
            date_mask = f"{date[:7]}-"
            period_exps = self.exp_repo.get_all_like(like={"expense_date": date_mask})
        spent = sum(int(exp.amount) for exp in period_exps)
        print(spent)
        self.budget_repo.update_attr(self.period_to_row[period]+1,"sum",f'{spent}')
        
      
        