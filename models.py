import sqlite3
import random

class Schema:
    def __init__(self):
        self.conn = sqlite3.connect('essensplan.db')
        self.create_dishes_table()
        self.create_days_table()
        self.create_ingredients_table()
        self.create_tags_table()
        self.create_taggedDishes_table()

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    def create_dishes_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS "Dishes" (
          dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          countCooked INTEGER,
          tag TEXT,
          lastCooked TEXT
        );
        """
        self.conn.execute(query)

    def create_tags_table(self):

            query = """
            CREATE TABLE IF NOT EXISTS "Tags" (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
            );
            """
            self.conn.execute(query)

    def create_taggedDishes_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS "TaggedDishes" (
          tag_id INTEGER,
          dish_id INTEGER
        );
        """
        self.conn.execute(query)


    def create_ingredients_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Ingredients" (
          dish_id INTEGER,
          name TEXT,
          amount FLOAT,
          unit TEXT
        );
        """
        self.conn.execute(query)

    def create_days_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS "Days" (
          date STRING,
          dish_id INTEGER
        );
        """

        self.conn.execute(query)

class Dishes:
    TABLENAME = "Dishes"
 
    # Erstellen des Objekts
    def __init__(self):
        self.conn = sqlite3.connect('Essensplan.db')
        self.conn.row_factory = sqlite3.Row

    # Schließen des Objekts
    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    # Gericht erstellen
    def create(self, params):
        params["countCooked"] = random.randint(0, 100)
        query = f'insert into {self.TABLENAME} ' \
               f'(name, countCooked, lastCooked) ' \
               f'values ("{params["name"]}",' \
               f'"{params["countCooked"]}", "")'
        result = self.conn.execute(query)
        dish_id = self.conn.execute('select last_insert_rowid();')
        return dish_id.lastrowid


    # Gericht löschen
    def delete(self, item_id):
        query = f"DELETE FROM {self.TABLENAME} " \
               f"WHERE dish_id = {item_id}"
        return self.conn.execute(query)


    # Gericht überarbeiten
    def update(self, item_id, update_dict):
        """
        column: value
        Title: new title
        """
        # Automatisches erstellen des UPDATE-Statements. Lief aber bisher nicht!
        # set_query = [f'{column} = {value}'
        #              for column, value in update_dict.items()]
        # for column, value in update_dict.items():
        #     print("{0} - {1}".format(column, value))
        #     set_query = column + ' = "' + value + '"'
        # print(set_query)
        # query = f"UPDATE {self.TABLENAME} " \
        #         f"SET {set_query} " \
        #         f"WHERE dish_id = {item_id}"
        
        query = "UPDATE Dishes SET name = '{0}', countCooked = {1}, lastCooked = {2} WHERE dish_id = {3}".format(update_dict['name'], update_dict['countCooked'], update_dict['lastCooked'], item_id)
        # print(query)
        self.conn.execute(query)
        return query

    # Alle Gerichte zurückgeben
    def list(self):
        where_clause = ""
        query = f"SELECT dish_id, name, countCooked, lastCooked " \
                f"from {self.TABLENAME} " \
                f"{where_clause}" \
                f"ORDER BY name"
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                  for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result

    # Name eines Gerichtes zurückgeben
    def getDish(self, dish_id):
        where_clause = "WHERE dish_id = "+ str(dish_id)
        query = f"SELECT dish_id, name, countCooked " \
                f"from {self.TABLENAME} " \
                f"{where_clause}"
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                  for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result




class Dish:
    def __init__(self):
        # name, ingredients, countCooked
        self.name = ""
        self.ingredients = ""
        self.countCooked = 0
        self.lastCooked = ""
        

class Ingredient:
    def __init__(self, dish_id):
        # dish_id, name, unit, amount
        self.dish_id = dish_id
        self.name = ""
        self.amount = 0.0
        self.unit = ""

class Ingredients:
    TABLENAME = "Ingredients"
 
    # Erstellen des Objekts
    def __init__(self):
        self.conn = sqlite3.connect('Essensplan.db')
        self.conn.row_factory = sqlite3.Row

    # Schließen des Objekts
    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    # Zutat erstellen
    def create(self, params):
        params["countCooked"] = random.randint(0, 100)
        query = f'insert into {self.TABLENAME} ' \
               f'(name, amount, unit, dish_id) ' \
               f'values ("{params["name"]}",' \
               f'{params["amount"]},"{params["unit"]}", {params["dish_id"]})'
        
        result = self.conn.execute(query)
        return result.fetchone()

    # Zutat löschen
    def delete(self, dish_id, name):
        query = f"DELETE FROM {self.TABLENAME} " \
               f"WHERE dish_id = {dish_id} AND name = '{name}'"
        self.conn.execute(query)


    # Zutat überarbeiten
    def update(self, name, dish_id, update_dict):

        set_query = [f'{column} = {value}'
                     for column, value in update_dict.items()]
        for column, value in update_dict.items():
            set_query = column + ' = "' + value + '"'

        query = f"UPDATE {self.TABLENAME} " \
                f"SET {set_query} " \
                f"WHERE dish_id = {item_id} AND name = '{name}'"
        print(query)
        self.conn.execute(query)

    # Alle Zutaten für ein Gericht zurückgeben
    def list(self, dish_id):
        where_clause = "WHERE dish_id = {0}".format(dish_id)
        query = f"SELECT dish_id, name, amount, unit " \
                f"from {self.TABLENAME} " \
                f"{where_clause}" \
                f" ORDER BY name"
        # print("Ingredients->list(): " + query)
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                  for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result


class Day:
    def __init__(self, year,month,day, dish_id, hasDish=False, isToday=False):
        self.date = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)
        self.year = year
        self.month = month
        self.day = day
        self.dish_id = dish_id
        self.hasDish = hasDish
        self.isToday = isToday

class Days:
    TABLENAME = "Days"
 
    # Erstellen des Objekts
    def __init__(self):
        self.conn = sqlite3.connect('Essensplan.db')
        self.conn.row_factory = sqlite3.Row

    # Schließen des Objekts
    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    # Gericht einem Tag zuweisen
    def create(self, params):
        day = params["day"]
        dish_id = params["dish_id"]
        # query = f'insert into {self.TABLENAME} ' \
        #        f'(name, ingredients, countCooked) ' \
        #        f'values ("{params["name"]}",' \
        #        f'"{params["ingredients"]}","{params["countCooked"]}")'

        query = f"insert into {self.TABLENAME} " \
               f"(date, dish_id) "\
               f"values ('{day}','{dish_id}')"
        result = self.conn.execute(query)
        self.conn.commit()
        return result.fetchone()

    # Gericht von einem Tag löschen
    def delete(self, params):
        date = params["day"]
        dish_id = params["dish_id"]
        query = f"DELETE FROM {self.TABLENAME} " \
               f"WHERE date = '{date}'"

        self.conn.execute(query)

     # Gerichte an einem Tag zurückgeben
    def list(self, date):

        # where_clause = ""
        query = f"SELECT Days.dish_id, Dishes.name " \
                f"from {self.TABLENAME} LEFT OUTER JOIN Dishes ON {self.TABLENAME}.dish_id = Dishes.dish_id " \
                f"WHERE Days.date = '{date}'"
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                  for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result

class Tags:
    """ Alle verfügbaren Tags """
    TABLENAME = "Tags"

    # Erstellen des Objekts
    def __init__(self):
        self.conn = sqlite3.connect('Essensplan.db')
        self.conn.row_factory = sqlite3.Row

    # Schließen des Objekts
    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    # Ein Tag erstellen
    def create_tag(self, params):
        # tag_id: int
        # name: string
        name = params["tag"]
        # query = f'insert into {self.TABLENAME} ' \
        #        f'(name, ingredients, countCooked) ' \
        #        f'values ("{params["name"]}",' \
        #        f'"{params["ingredients"]}","{params["countCooked"]}")'

        query = f"insert into {self.TABLENAME} " \
                f"(name) "\
                f"values ('{name}')"
        result = self.conn.execute(query)
        for row in result:
            print(row['tag_id'])
        self.conn.commit()
        return result.fetchone()

    # Ein Tag löschen
    def delete_tag(self, params):
        # Tabelle für Tag und Dishes: TaggedDishes
        # Tabelle für Tags: Tags
        tag_id = params["tag_id"]

        # Zuweisungen zu Gerichten löschen
        query = f"DELETE FROM TaggedDishes " \
                f"WHERE tag_id = '{tag_id}'"
        self.conn.execute(query)

        # Tag löschen
        query = f"DELETE FROM {self.TABLENAME} " \
                f"WHERE tag_id = '{tag_id}'"
        self.conn.execute(query)
        
        return True

        # Tags zurückgeben

    def list_tags(self):

        # where_clause = ""
        query = f"SELECT Tags.tag_id, Tags.name " \
                f"from {self.TABLENAME} ORDER BY Tags.name"
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                    for i, column in enumerate(result_set[0].keys())}
                    for row in result_set]
        return result

    def get_name(self, tag_id):

        # where_clause = ""
        query = f"SELECT Tags.tag_id, Tags.name " \
                f"from {self.TABLENAME} " \
                f"WHERE tag_id = '{tag_id}'"
        print(query)
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                    for i, column in enumerate(result_set[0].keys())}
                    for row in result_set]
        return result

    def get_tag_id(self, tag_name):

        # where_clause = ""
        query = f"SELECT Tags.tag_id " \
                f"from {self.TABLENAME} " \
                f"WHERE name = '{tag_name}'"

        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                    for i, column in enumerate(result_set[0].keys())}
                    for row in result_set]
        return result


class TaggedDishes:
    """ n zu n Gerichte <> Tags """
    TABLENAME = "TaggedDishes"

    # Erstellen des Objekts
    def __init__(self):
        self.conn = sqlite3.connect('Essensplan.db')
        self.conn.row_factory = sqlite3.Row

    # Schließen des Objekts
    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()
    
    def assign_tag_to_dish(self, dish_id, tag_id):
        # tag_id INTEGER,
        # dish_id INTEGER
        tags = Tags()
        
        # Anzahl der Einträge mit der Kombination holen, um festzustellen, ob sie schon vorhanden ist.
        query = "SELECT count(*) FROM {0} WHERE dish_id = {1} AND tag_id = {2}".format(self.TABLENAME, dish_id, tag_id)
        # print(query)
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                    for i, column in enumerate(result_set[0].keys())}
                    for row in result_set]
        
        # print(result[0]['count(*)'])

        # Wenn 0, dann gibt es die Kombination noch nicht und wird angelegt, alternativ ist nichts zu tun.
        if result[0]['count(*)'] == 0:
            query = 'insert into {0} (dish_id, tag_id) values ("{1}", "{2}")'.format(self.TABLENAME, dish_id, tag_id)
            # print(query)
            return self.conn.execute(query)
        return True
    
    def remove_tag_from_dish(self, dish_id, tag_id):
        # tag_id INTEGER,
        # dish_id INTEGER
        tags = Tags()
        
        
        query = "DELETE FROM {0} WHERE dish_id = {1} AND tag_id = {2}".format(self.TABLENAME, dish_id, tag_id)
        # print(query)
        return self.conn.execute(query).fetchall()
        

    def list(self, dish_id):
        """ Gibt alle Tags für ein Gericht zurück """

        where_clause = "WHERE dish_id = {0}".format(dish_id)
        query = f"SELECT tag_id " \
                f"from {self.TABLENAME} " \
                f"{where_clause}"
        # print(query)
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                  for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result


    def list_with_names(self, dish_id):
        """ Gibt alle Tags für ein Gericht zurück """

        where_clause = "WHERE dish_id = {0}".format(dish_id)
        query = f"SELECT * " \
                f"from {self.TABLENAME} " \
                f"JOIN Tags ON {self.TABLENAME}.tag_id = Tags.tag_id " \
                f"{where_clause};"
        # print(query)
        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                  for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result
        