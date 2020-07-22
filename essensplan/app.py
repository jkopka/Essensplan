import requests

from flask import request, flash
from flask import render_template
from flask import Flask, url_for, redirect

from models import Schema
from models import Dishes
from models import Day
from models import Days
from models import Ingredients
from models import Tags
from models import TaggedDishes

from customFunctions import getMonday,addTodoListToWunderlist
from datetime import timedelta
from datetime import date
from datetime import datetime
from calendar import month_name

# Datenbank: SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Usermanagement: Flask-User
from flask_user import login_required, UserManager, UserMixin

import operator # Für die Wunderlist-Funktion: Sortierung




@app.route("/displayWeek", methods=["POST", "GET"])
def displayWeek():
    try:
        choosenDate = datetime.strptime(request.args.get('date', ''), "%Y-%m-%d").date()
    except:
        choosenDate = date.today()
    monday = getMonday(choosenDate)
    try:
        message = request.args.get('message', '')
    except KeyError:
        message = ''
    year = monday.strftime("%Y")
    monthNames = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    monthNumbers = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    month = monthNames[monday.month-1]
    day = monday.day
    week_number = choosenDate.isocalendar()[1]
    week = [(monday+timedelta(days=0)).day, (monday+timedelta(days=1)).day, (monday+timedelta(days=2)).day, (monday+timedelta(days=3)).day, (monday+timedelta(days=4)).day, (monday+timedelta(days=5)).day, (monday+timedelta(days=6)).day]
    weekdays = {(monday+timedelta(days=0)).day:'Montag', (monday+timedelta(days=1)).day:'Dienstag', (monday+timedelta(days=2)).day:'Mittwoch', (monday+timedelta(days=3)).day:'Donnerstag', (monday+timedelta(days=4)).day:'Freitag', (monday+timedelta(days=5)).day:'Samstag', (monday+timedelta(days=6)).day:'Sonntag'}
    dishes = Dishes()
    daysObject = Days()
    # FEATURE: Abrufen des zugewiesenen Gerichts für den Tag
    # In der Schleife werden die dishes
    days = {}
    for day in range(0,7):
        actualDay = monday+timedelta(days=day)
        dishesperDay = daysObject.list(actualDay)
        
        if len(dishesperDay) != 0:
            days[actualDay.day] = Day(year, int(actualDay.strftime("%m")), actualDay.strftime("%d"), dishesperDay, True)
        else:
            days[actualDay.day] = Day(year, int(actualDay.strftime("%m")), actualDay.strftime("%d"), dishesperDay, False)
        if actualDay == datetime.now().date():
            days[actualDay.day].isToday = True

    if message:
        flash(message)
    
    output = render_template('index.html', linkCreateDish=url_for('formCreateDish'), linkchooseDish=url_for('formChooseDish'), nextWeek=(choosenDate+timedelta(days=7)).strftime("%Y-%m-%d"), lastWeek=(choosenDate+timedelta(days=-7)).strftime("%Y-%m-%d"), week_number=week_number, choosenDatum=monday, year=year, monthName=month, monthNames=monthNames, monthNumbers=monthNumbers, week=week, weekdays=weekdays, month=monday.month-1, days=days, dishes=dishes)
    return output




@app.route("/dishes")
def listDishes():
    dishes = Dishes()
    returnText = ""
    listDishes = dishes.list()
    del dishes
    countDishes = len(listDishes)
    # returnText = returnText + "Anzahl Dishes: " + str(countDishes) + "<br />"

    ## Für das Tagging:
    # taggedDishes = TaggedDishes()
    # for index, item in enumerate(listDishes):
    #     # if listDishes[index]["lastCooked"]:
    #     #     print(datetime.strptime(listDishes[index]["lastCooked"], "%Y-%m-%d").strftime("%d-%m-%Y"))
    #     tag_for_dish = taggedDishes.list_with_names(listDishes[index]['dish_id'])
    #     listDishes[index]['tags'] = tag_for_dish
    #     for tag in listDishes[index]['tags']:
    #         print(tag)
        

    returnTemplate = render_template('dishes.html', dishes=listDishes)
    # for dish in listDishes:
    #     deleteLink = url_for('deleteDish') + "?id=" + str(dish["dish_id"])
    #     returnText = returnText + "<a href='" + deleteLink + "'> "  + dish["name"] + "</a><br />"

    return returnTemplate
    # return "Liste der verfügbaren Dishes"


@app.route("/formCreateDish")
def formCreateDish():
    tags = Tags()
    allTags = tags.list_tags()
    countTags = len(allTags)
    return render_template('formCreateDish.html', tags=allTags, countTags=countTags)


@app.route("/formEditDish", methods=["POST", "GET"])
def formEditDish():
    """ Zeigt ein Formular zur bearbeitung eines Gerichts an. Parameter: dish_id """
    
    # Abfragen, ob Daten übergeben wurden
    if request:
        dish_id = request.args.get('dish_id', '')
    else:
        return "Error"

    # Falls dish_id als String übergeben wurde -> in Integer umwandeln
    
    if type(dish_id) == str:
        dish_id = int(dish_id)

    # Gericht & Tags mit Namen laden
    dishes = Dishes()
    dish = dishes.getDish(dish_id)[0]
    taggedDishes = TaggedDishes()
    tag_for_dish = taggedDishes.list_with_names(dish['dish_id'])
    dish['tags'] = tag_for_dish
    
    # Allgemeine Tags laden
    tags = Tags()
    allTags = tags.list_tags()
    countTags = len(allTags)

    # Zutaten für das Gericht laden
    ingredientsAll = Ingredients()
    ingredients = ingredientsAll.list(dish_id)

    # Alle Namen und Einheiten der Zutaten laden
    suggestions = ingredientsAll.get_suggestions()
    # print(suggestions)

    # Tags selektieren
    for index in range(len(allTags)):
        for tag2 in tag_for_dish:
            if allTags[index]['tag_id'] == tag2['tag_id']:
                allTags[index]['selected'] = " selected"

    # Template füllen und zurückgeben
    return render_template('formEditDish.html', allTags=allTags, countTags=countTags, dish=dish, ingredients=ingredients, ingredientsCount=len(ingredients), suggestions=suggestions)


@app.route("/chooseDish", methods=["POST", "GET"])
def formChooseDish():
    dishes = Dishes()
    returnText = ""
    choosenDate = request.args.get('choosen_date')
    listDishes = dishes.list()
    print(choosenDate)
    return render_template('formChooseDish.html', dishes=listDishes, date=choosenDate)


@app.route("/createDish", methods=["POST", "GET"])
def createDish():
    params = {}
    if request:
        params["name"] = request.args.get('name', '')
        params["note"] = request.args.get('note', '')
        params["ingredients"] = request.args.get('ingredients', '')
        params["countCooked"] = 0
        params["tags"] = request.args.get('tags','')
        params["tags"] = request.args.getlist('tags')
        tags_list = []

        # Datenbank öffnen
        tags = Tags()

        for tag_name_request in params["tags"]:
            tag_id = tags.get_tag_id(tag_name_request)[0]['tag_id']
            print("Tag_name: {0}".format(tag_name_request))
            print("   Tag_id ist: {0}".format(tag_id))
            if not tag_id:
                print("   Tag erstellen")
                tag_id = tags.create_tag("tag_name_request")
            tags_list.append(tag_id)
        
        print("")
        # Datenbank und Tabelle schließen
        del tags

        # Datenbank öffnen & Gericht erstellen
        dishes = Dishes()
        dish_id = dishes.create(params)
        del dishes
        # Zum testen hier die feste dish_id 22, somit wird nicht jedes mal ein Gericht angelegt
        # dish_id = 22
        
        if dish_id:
            taggedDishes = TaggedDishes()
            for tag_id in tags_list:
                print("Zuweisung: {0} zu {1}".format(dish_id, tag_id))
                taggedDishes.assign_tag_to_dish(dish_id, tag_id)
            return "Erfolgreich<br /><a href=\"" + url_for('listDishes') + "\">Gerichte anzeigen</a>"
    else:
        return "Fehler"


@app.route("/editDish", methods=["POST"])
def editDish():
    params = {}
    if request:
        params["dish_id"] = request.form.get('dish_id', '')
        params["name"] = request.form.get('name', '')
        params["note"] = request.form.get('note', '')
        # params["ingredients"] = request.args.get('ingredients', '')
        params["countCooked"] = "0"
        params["lastCooked"] = "2019-01-01"
        # params["tags"] = request.args.get('tags','')
        params["tags"] = request.form.getlist('tags')
        tags_list = []

        # print(params["tags"])

        # Datenbank öffnen
        tags = Tags()

        for tag_name_request in params["tags"]:
            tag_id = tags.get_tag_id(tag_name_request)[0]['tag_id']
            # print("Tag_name: {0}".format(tag_name_request))
            # print("   Tag_id ist: {0}".format(tag_id))
            if not tag_id:
                # print("   Tag erstellen")
                tag_id = tags.create_tag("tag_name_request")
            tags_list.append(tag_id)
        
        # Übergabeparameter zusammenstellen
        dish_stuff = {}
        # dish_stuff['dish_id'] = params['dish_id']
        dish_stuff['name'] = params['name']
        dish_stuff['note'] = params['note'].splitlines()
        # dish_stuff['ingredients'] = params['ingredients']
        dish_stuff['countCooked'] = params['countCooked']
        # dish_stuff['lastCooked'] = params['lastCooked']
        dish_stuff['lastCooked'] = params['lastCooked']
        
        # Datenbank und Tabelle schließen
        del tags

        # Datenbank öffnen & Gericht erstellen
        dishes = Dishes()
        returnValue = dishes.update(params["dish_id"], dish_stuff)
        del dishes
        # Zum testen hier die feste dish_id 22, somit wird nicht jedes mal ein Gericht angelegt
        # dish_id = 22
        
        
        taggedDishes = TaggedDishes()
        # print(tags_list)
        existing_tags = taggedDishes.list(params["dish_id"])
        # print("Existing Tags: {0}".format(existing_tags))
        # print("tags_list: {0}".format(tags_list))
        for tag_id in tags_list:
            # print([item for item in existing_tags if item["tag_id"] == tag_id])
            if not [item for item in existing_tags if item["tag_id"] == tag_id]:
                # print("tag_id: {0} - existing_tag: {1}".format(tag_id, existing_tag))
                # print("Zuweisung: {1} zu {0}".format(params["dish_id"], tag_id))
                taggedDishes.assign_tag_to_dish(params["dish_id"], tag_id)
            
        for existing_tag in existing_tags:
            if not existing_tag['tag_id'] in tags_list:
                # print("Zuweisung löschen: {1} zu {0}".format(params["dish_id"], existing_tag['tag_id']))
                taggedDishes.remove_tag_from_dish(params["dish_id"], existing_tag['tag_id'])
        return redirect(url_for('showDish',dish_id=params["dish_id"]))


@app.route("/assignDish", methods=["POST", "GET"])
def assignDish():
    dish_id = int(request.args.get('dish_id', ''))
    choosen_date = request.args.get('choosen_date', '')
    if dish_id and choosen_date:
        days = Days()
        dishes = Dishes()
        params = {}
        params["dish_id"] = int(dish_id)
        params["day"] = choosen_date
        update_dict = {}
        print(choosen_date)
        update_dict["lastCooked"] = choosen_date
        update_dict['countCooked'] = 0
        dish = dishes.getDish(dish_id)
        update_dict["name"] = dish[0]["name"]
        days.create(params)
        # dishes.update(dish_id, update_dict)
        return redirect(url_for('displayWeek',date=choosen_date))
    else:
        return "0"


@app.route("/removeDish", methods=["POST", "GET"])
def removeDish():
    dish_id = int(request.args.get('dish_id', ''))
    choosen_date = request.args.get('choosen_date', '')
    if dish_id and choosen_date:
        days = Days()
        params = {}
        params["dish_id"] = int(dish_id)
        params["day"] = choosen_date
        returnValue = days.delete(params)
        return redirect(url_for('displayWeek',date=choosen_date))
    else:
        return redirect(url_for('displayWeek',date=choosen_date))


@app.route("/deleteDish", methods=["POST", "GET"])
def deleteDish():
    dishes = Dishes()
    params = {}
    print(request.form)
    if request:
        print(dishes.delete(request.args.get('dish_id', '')))
        return redirect(url_for('listDishes'))
    else:
        return "Fehler! <br /><a href\"" + url_for('listDishes') + "\">Liste</a>"


@app.route("/dish/<int:dish_id>")
def showDish(dish_id):
    if type(dish_id) is int:
        dishes = Dishes()
        dish = dishes.getDish(dish_id)[0]
        taggedDishes = TaggedDishes()
        tag_for_dish = taggedDishes.list_with_names(dish['dish_id'])
        dish['tags'] = tag_for_dish
        if dish['note']:
            dish['note'] = dish['note'].replace('\n', '<br>')
        else:
            dish['note'] = ''
        for tag in dish['tags']:
            print(tag)
        ingredientsAll = Ingredients()
        ingredients = ingredientsAll.list(dish_id)
        return render_template('dish.html', dish=dish, ingredients=ingredients, ingredientsCount=len(ingredients))
    else:
        returnText = "Detailansicht eines Gerichts: Fehler"

    
    # return returnText


@app.route("/createIngredient", methods=["POST", "GET"])
def createIngredient():
    ingredients = Ingredients()
    params = {}
    if request:
        params["dish_id"] = request.args.get('dish_id', '')
        params["name"] = request.args.get('name', '')
        params["amount"] = request.args.get('amount', '')
        params["unit"] = request.args.get('unit', '')
        dish_id = ingredients.create(params)
        return redirect(url_for('formEditDish', dish_id=params["dish_id"]))
    else:
        return "Fehler"

@app.route("/deleteIngredient", methods=["POST", "GET"])
def deleteIngredient():
    ingredients = Ingredients()
    params = {}
    if request:
        dish_id = request.args.get('dish_id', '')
        name = request.args.get('name', '')
        ingredients.delete(dish_id, name)
        ingredients.__del__
        del(ingredients)
        # return redirect(url_for('getTags'), msg='Tag created')
        return redirect(url_for('formEditDish', dish_id=dish_id))
        # return "{0}".format(params)
    else:
        return "Fehler"

@app.route("/create_tag", methods=["POST", "GET"])
def create_tag():
    tags = Tags()
    params = {}
    if request:
        params["tag"] = request.args.get('tag', '')
        if len(params["tag"]) == 0:
            return redirect(url_for('getTags'))

        tag_id = tags.create_tag(params)
        print(tag_id)
        # return "yay {0}".format(params["tag"])
        # return redirect(url_for('getTags', msg='Tag {0} wurde hinzugefügt.'.format(params['name'])))
        return redirect(url_for('getTags'))
    else:
        return "Fehler"
    return "Fehler"

@app.route("/tags", methods=["POST", "GET"])
def getTags():
    has_message = False
    if request:
        if request.args.get('msg', ''):
            has_message = request.args.get('msg', '')
        # return redirect(url_for('listDishes'))
    else:
        has_message = False
        return "Fehler! <br /><a href\"" + url_for('listDishes') + "\">Liste</a>"
    tags = Tags()
    allTags = tags.list_tags()
    # if len(allTags) > 0:
    #     for tag in allTags:
    #         print(tag)
    
    return render_template('tags.html', tags=allTags, has_message=has_message)

@app.route("/deletetag", methods=["POST", "GET"])
def deleteTag():
    tags = Tags()
    params = {}
    if request:
        # params["tag"] = request.args.get('tag', '')
        params['tag_id'] = request.args.get('tag_id', '')
        print(params)
        tags.delete_tag(params)
        tags.__del__
        del(tags)
        # return redirect(url_for('getTags'), msg='Tag created')
        return redirect(url_for('getTags'))
        # return "{0}".format(params)
    else:
        return "Fehler"

@app.route("/addToWunderlist", methods=["POST", "GET"])
def addToWunderlist():
    # Alle Zutaten der Gerichte der angezeigten Woche zu Wunderlist hinzufügen
    # 
    # input: Angezeigte Woche
    # 
    # -> Alle Gerichte der Woche holen
    # 
    # -> Alle Zutaten der Gerichte sammeln und gleiche Zutaten kombinieren
    # 
    # -> Zutaten per API zu Wunderlist hinzufügen
    try:
        choosenDate = datetime.strptime(request.args.get('date', ''), "%Y-%m-%d").date()
    except:
        choosenDate = date.today()
    monday = getMonday(choosenDate)
    day = monday.day
    year = monday.strftime("%Y")
    # week = [(monday+timedelta(days=0)).day, (monday+timedelta(days=1)).day, (monday+timedelta(days=2)).day, (monday+timedelta(days=3)).day, (monday+timedelta(days=4)).day, (monday+timedelta(days=5)).day, (monday+timedelta(days=6)).day]
    # weekdays = {(monday+timedelta(days=0)).day:'Montag', (monday+timedelta(days=1)).day:'Dienstag', (monday+timedelta(days=2)).day:'Mittwoch', (monday+timedelta(days=3)).day:'Donnerstag', (monday+timedelta(days=4)).day:'Freitag', (monday+timedelta(days=5)).day:'Samstag', (monday+timedelta(days=6)).day:'Sonntag'}
    dishes = Dishes()
    dishes_for_wunderlist = {}
    daysObject = Days()
    ingredientsObject = Ingredients()
    html = "bla"
    ingredients_for_wunderlist = []
    ingredients = {}
    ingredients_obj = []
    for day in range(0,7):
        actualDay = monday+timedelta(days=day)
        dishesperDay = daysObject.list(actualDay)
        for dish in dishesperDay:
            # print(dish)
            dish_ingredients = ingredientsObject.list(dish['dish_id'])
            for ing in dish_ingredients:
                if not ing["amount"]:
                    continue
                amount = ing['amount']
                if amount % 1 == 0:
                    amount = int(amount)
                ing['amount'] = amount
                element_index = next((index for (index, d) in enumerate(ingredients_obj) if d["name"] == ing['name']), None)
                if element_index:
                    print("Gefunden" + ing['name'])
                    ingredients_obj[element_index]['amount'] += amount
                else:
                    ingredients_obj.append(ing)

    # Zutaten sortieren
    ingredients_obj.sort(key=operator.itemgetter('name'))

    for ing in ingredients_obj:
        if ing['unit'] + " " + ing['name'] in ingredients:
            ingredients[ing['unit'] + " " + ing['name']] += amount
        else:
            ingredients[ing['unit'] + " " + ing['name']] = amount
    for key, value in ingredients.items():
        if not addTodoListToWunderlist("{0} {1}".format(value, key)) == 201:
            return "Error!"
    
    # Test, der eine einzelne Todo erstellt
    # if not addTodoListToWunderlist("2.0 Stück Chilischote") == 201:
    #          return "Error!"
    return redirect(url_for('displayWeek', message='Zutaten wurden zur Wunderlist hinzugefügt'))
        

if __name__ == "__main__":
    Schema()
    app.run(host='0.0.0.0', debug=True)
