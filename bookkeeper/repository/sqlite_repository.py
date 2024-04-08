"""
Модуль описывает репозиторий, работающий с sqlite
"""

import sqlite3
from typing import Any
from inspect import get_annotations
from repository.abstract_repository import AbstractRepository, T

class SQLiteRepository(AbstractRepository[T]):
    """_summary_
    Args:
        AbstractRepository (_type_): _description_
    """
    obj_cls: type

    def __init__(self, db_name: str, cls: type) -> None:
        self.db_name = db_name
        self.obj_cls = cls
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
    
        self.cls = cls

    def add(self, obj: T) -> int:
        """
        Add a new object to the database.

        Parameters:
        obj (T): The object to add to the database.

        Returns:
        int: The primary key (pk) assigned to the object in the database.
        """
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        
        try:
            with sqlite3.connect(self.db_name) as connection:
                cur = connection.cursor()
                cur.execute('PRAGMA foreign_keys = ON')
                cur.execute(
                    f'INSERT INTO {self.table_name} ({names}) VALUES ({p})',
                    values
                )
                obj.pk = int(cur.lastrowid)
        except sqlite3.IntegrityError as e:
            print(f"Error: {e}. Primary Key is not unique.")
            # Действия при неуникальном Primary Key
            
        connection.close()
        return obj.pk


    def get(self, pk: int) -> T | None:
        """
        Get an object by its primary key.

        Args:
            pk (int): The primary key identifier.

        Returns:
            T | None: The retrieved object or None if not found.

        Raises:
            sqlite3.Error: If an error occurs during the query execution.
        """
        try:
            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor()
                result = cursor.execute(f'SELECT * FROM {self.table_name} '
                + f'WHERE ROWID=={pk}').fetchone()
                if result is None:
                    return None
                obj: T = self._generate_object(pk,result)
                return obj
        except sqlite3.Error as e:
            print(f"An error occurred while fetching the object: {e}")
            return None

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Get all records based on a specified condition.

        Args:
            where (dict[str, Any] | None): The condition as a dictionary {'field_name': value}.
                If not specified (default is None), return all records.

        Returns:
            list[T]: List of records that meet the specified condition.

        Raises:
            sqlite3.Error: If an error occurs during the query execution.
        """
        try:
            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor()
                if where is None:
                    results = cursor.execute(
                        f'SELECT ROWID, * FROM {self.table_name} '
                    ).fetchall()
                else:
                    fields = " AND ".join([f"{f} LIKE ?" for f in where.keys()])
                    results = cursor.execute(
                        f'SELECT ROWID, * FROM {self.table_name} '
                        + f'WHERE {fields}',
                        list(where.values())
                    ).fetchall()
            return [self._generate_object(r[0], r[1:]) for r in results]
        except sqlite3.Error as e:
            print(f"An error occurred while fetching records: {e}")
            return []  # Return an empty list in case of an error
        finally:
            connection.close()
        
    def get_all_like(self, like: dict[str, str]) -> list[T]:
        values = [f"%{v}%" for v in like.values()]
        where = dict(zip(like.keys(), values))
        return self.get_all(where=where)

    def update(self, obj: T) -> None:
        """
        Update a record in the database based on the object attributes.

        Args:
            obj: The object containing the updated values.

        Raises:
            sqlite3.Error: If an error occurs during the update process.
        """
        try:
            values = [getattr(obj, x) for x in self.fields]
            setter = [f'{col} = {val}' for col, val in zip(self.fields, values)]
            upd_stm = ', '.join(setter)

            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor() 
                query = f'UPDATE {self.table_name} SET {upd_stm} WHERE ROWID == {obj.pk}'
                cursor.execute(query)
        except sqlite3.Error as e:
            print(f"An error occurred while updating the record: {e}")
        finally:
            connection.close()

    
    def update_attr(self, pk:int, attr:str, new_val:str) -> None:
        """
        Update a record in the database based on the object attributes.

        Args:
            obj: The object containing the updated values.

        Raises:
            sqlite3.Error: If an error occurs during the update process.
        """
        try:
            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor() 
                query = f'UPDATE {self.table_name} SET {attr} = {new_val} WHERE ROWID == {pk}'
                print(query)
                cursor.execute(query)
        except sqlite3.Error as e:
            print(f"An error occurred while updating the record: {e}")
        finally:
            connection.close()

    def delete(self, pk: int) -> None:
        """
        Delete a record by primary key.
        
        Args:
            pk (int): Primary key of the record to be deleted.

        Raises:
            sqlite3.Error: If an error occurs during the deletion process.
        """
        try:
            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor() 
                cursor.execute(f'DELETE FROM {self.table_name} WHERE ROWID == {pk}')
        except sqlite3.Error as e:
            print(f"An error occurred while deleting the record: {e}")
        finally:
            connection.close()

    def delete_all(self) -> None:
        """
        Delete all records in the table.

        Raises:
            sqlite3.Error: If an error occurs during the deletion process.
        """
        try:
            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor()
                cursor.execute('DELETE FROM ?',(self.table_name,))
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            connection.close()

    def _get_attribute_type(self,attr: Any) -> str:
        """
        Determine the data type of the attribute.

        Args:
            attr (Any): The attribute whose data type is to be determined.

        Returns:
            str: The data type of the attribute.
        """
        if isinstance(attr, int):
            return 'INTEGER'
        return 'TEXT'
    
    def _generate_object(self, rowid: int, row: tuple[Any]) -> T:
        """
        Fills attributes of object according to the results.

        Args:
            result (Any): Result of the DB query.

        Returns:
            T: Filled object.

        Raises:
            IndexError: If index is out of range while accessing results.
        """
        try:
            kwargs = dict(zip(self.fields, row))
            obj = self.obj_cls(**kwargs)
            obj.pk = rowid
            return obj
        except IndexError as e:
            print(f"An error occurred while generating the object: {e}")
            return None
       

            
