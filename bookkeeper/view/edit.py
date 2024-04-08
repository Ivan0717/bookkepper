"""
Widget for editing pane
"""

from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QComboBox
from models.category import Category
from models.expense import Expense
from repository.sqlite_repository import SQLiteRepository
from .edit_ctg import EditCtgWindow
from collections.abc import Callable

def set_data(box: QComboBox, cats: list[str]) -> None:
    for cat in cats:
        box.addItem(cat)

class EditWidget(QWidget):
    def __init__(self, 
                category_repo: SQLiteRepository[Category],
                exp_repo: SQLiteRepository[Expense],
                exp_adder: Callable[[str, int], None],) -> None:
        super().__init__()
        self.category_repo = category_repo
        self.exp_repo = exp_repo
        self.exp_adder = exp_adder

        layout = QtWidgets.QVBoxLayout()

        sum_label = QtWidgets.QLabel("Сумма")
        cat_label = QtWidgets.QLabel("Категория")
        add_button = QtWidgets.QPushButton("Добавить")
        cat_edit_button = QtWidgets.QPushButton("Редактировать")
        self.sum_line = QtWidgets.QLineEdit("0")
        self.cats_box = QtWidgets.QComboBox()
        glayout = QtWidgets.QGridLayout()

        glayout.addWidget(sum_label, 0, 0)
        glayout.addWidget(self.sum_line, 0, 1)
        glayout.addWidget(cat_label, 1, 0)
        glayout.addWidget(self.cats_box, 1, 1)
        glayout.addWidget(cat_edit_button, 1, 2)
        glayout.addWidget(add_button, 2, 1)
        gwidget = QWidget()
        gwidget.setLayout(glayout)
        layout.addWidget(gwidget)

        self.cat_list = [result.name for result in category_repo.get_all()]  
        
        set_data(self.cats_box, self.cat_list)

        cat_edit_button.clicked.connect(self.open_window)
        add_button.clicked.connect(self.add_expense)

        self.setLayout(layout)


    def open_window(self):
        self.edit_ctg = EditCtgWindow(self.category_repo)
        self.edit_ctg.show()

    def add_expense(self):
        self.exp_adder(self.sum_line.text(),
                self.cats_box.currentIndex()+1)