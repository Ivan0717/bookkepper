"""
Модуль содержит код, отвечающий за
запуск приложения.
"""
import sys
from PySide6.QtWidgets import QApplication
from view.main_view import MainWindow
from models.category import Category
from models.expense import Expense
from models.budget import Budget
from repository.sqlite_repository import SQLiteRepository

DB_NAME = 'bookkeeper.db'

if __name__ == '__main__':
    app = QApplication(sys.argv)

    category_repo = SQLiteRepository[Category](DB_NAME, Category)
    exp_repo = SQLiteRepository[Expense](DB_NAME, Expense)
    budget_repo = SQLiteRepository[Budget](DB_NAME, Budget)

    view = MainWindow(category_repo, exp_repo,budget_repo)
    view.show()
    app.exec()