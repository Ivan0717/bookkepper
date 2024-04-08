import sqlite3
from inspect import get_annotations
from models.category import Category
from models.expense import Expense
from models.budget import Budget
from utils import read_tree
from repository.sqlite_repository import SQLiteRepository

db_file ="bookkeeper.db"
for cls in [Category, Expense, Budget]:
    table_name = cls.__name__.lower()
    fields = get_annotations(cls, eval_str=True)
    print(fields)
    print("ass")
    fields.pop('pk')
    with sqlite3.connect(db_file) as con:
        cur = con.cursor()
        cur.execute(f"CREATE TABLE {table_name}({', '.join(fields.keys())})")
    con.close()

cat_repo = SQLiteRepository[Category](db_file,cls=Category)
cats = ["Продукты", "Хозтовары","Кефир","Хлеб","Сладости","Сыр","Сметана","Книги","Телефон","Рыба"]

for cat in cats:
    ctg = Category(cat)
    cat_repo.add(ctg)
for cat in cat_repo.get_all():
    print(cat.name)
bud_repo = SQLiteRepository[Budget](db_file,cls=Budget)
bud_repo.add(Budget(period="day", budget=1000, sum=0))
bud_repo.add(Budget(period="week", budget=7000, sum=0))
bud_repo.add(Budget(period="month", budget=30000, sum=0))
