"""
Widget of editing categories
"""

from PySide6 import QtWidgets
from PySide6.QtWidgets import (QWidget, QListWidget)
from models.category import Category
from repository.sqlite_repository import SQLiteRepository

def set_data(table: QListWidget, data: list[str]) -> None:
    for ctg in data:
        table.addItem(ctg)
        table.takeItem


class EditCtgWindow(QWidget):
    def __init__(self, category_repo: SQLiteRepository[Category]) -> None:
        super().__init__()

        self.setWindowTitle("Изменение категорий")
        self.glayout = QtWidgets.QGridLayout()
        self.category_repo = category_repo
        self.ctgs = [result.name for result in category_repo.get_all()]  
        self.input_old_ctg = self.ctgs[0]

        layout = QtWidgets.QVBoxLayout()
        self.label  = QtWidgets.QLabel("Категории")
        self.cat_add_button = QtWidgets.QPushButton("Добавить")
        self.cat_edit_button = QtWidgets.QPushButton("Редактировать")
        self.cat_delete_button = QtWidgets.QPushButton("Удалить")
        self.input = QtWidgets.QLineEdit("новая категория")
        self.input_old_ctg = QtWidgets.QLineEdit("старая категория")

        
        self.glayout.addWidget(self.label, 0, 0)
        self.glayout.addWidget(self.cat_add_button, 1, 0)
        self.glayout.addWidget(self.cat_delete_button, 2, 0)
        self.glayout.addWidget(self.cat_edit_button, 3, 0)
        self.glayout.addWidget(self.input, 4, 0)
        self.glayout.addWidget(self.input_old_ctg, 5, 0)
        

        self.cat_add_button.clicked.connect(self.add_category)
        self.cat_edit_button.clicked.connect(self.edit_category)
        self.cat_delete_button.clicked.connect(self.delete_category)

        gwidget = QWidget()
        gwidget.setLayout(self.glayout)
        layout.addWidget(gwidget)

        self.ctgs_widget = QtWidgets.QListWidget()
        set_data(self.ctgs_widget, self.ctgs)

        layout.addWidget(self.ctgs_widget)
        self.setLayout(layout)

    def delete_category(self) -> None:
        """ Вызывает удаление категории """
        print(self.ctgs)
        print(self.input_old_ctg.text())
        pk = self.ctgs.index(self.input_old_ctg.text())
        print(pk)
        self.ctgs.remove(self.input_old_ctg.text())
        self.category_repo.delete(pk+1)
        print(self.category_repo.get_all())

    def add_category(self) -> None:
        """ Вызывает добавление категории """
        self.ctgs.append(self.input.text())

    def edit_category(self) -> None:
        """ Вызывает изменение категории """
        pk = self.ctgs.index(self.input_old_ctg.text())
        self.ctgs.remove(self.input_old_ctg.text())
        self.category_repo.delete(pk+1)
        self.ctgs.append(self.input.text())
        self.category_repo.add(Category(self.input.text()))
    




