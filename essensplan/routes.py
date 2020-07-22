from flask import request, render_template, make_response, url_for, redirect, render_template_string, flash
from flask import current_app as app
from datetime import datetime as dt
from .models import db, User, Dish, Ingredient, Tag, Days
from flask_user import login_required, current_user

@app.route("/users", methods=["POST", "GET"])
@login_required
def create_user():
    """Create a user."""
    # Daten abfragen
    username = request.args.get('user')
    email = request.args.get('email')
    password = request.args.get('password')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')


    if username and email:
        existing_user = User.query.filter(User.username == username or User.email == email).first()
        if existing_user:
            return make_response(f'{username} ({email}) already created!')
        new_user = User(username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        created=dt.now())  # Create an instance of the User class
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
    return render_template('users.html',
                           users=User.query.all(),
                           title="Show Users")


@app.route("/displayWeek", methods=["POST", "GET"])
@login_required
def displayWeek():
    from datetime import date, timedelta, datetime
    from .customFunctions import getMonday

    if 'date' in request.args:
        choosenDate = datetime.strptime(request.args.get('date', ''), "%Y-%m-%d").date()
    else:
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
    
    if week_number == date.today().isocalendar()[1]:
        date_title = 'Aktuelle Woche'
    elif week_number + 1 == date.today().isocalendar()[1]:
        date_title ='Letzte Woche'
    elif week_number - 1 == date.today().isocalendar()[1]:
        date_title ='Nächste Woche'
    else:
        date_title = 'Die Woche vom {0}.-{1}.{2}'.format(dt.strftime(monday, '%d'), dt.strftime(monday+timedelta(days=6), '%d.%m'), year)

    
    
    # Hier geht es mit den Daten los
    # dishes = Dishes()
    # daysObject = Days()

    # FEATURE: Abrufen des zugewiesenen Gerichts für den Tag
    # In der Schleife werden die dishes
    days = {}
    dishes = {}
    for day in range(0,7):
        actualDay = monday+timedelta(days=day)

        dishesperDay = Days.query.filter_by(date=actualDay,user_id=current_user.id)
        
        # if dishesperDay.count() != 0:
        #     days[actualDay.day] = Day(year, int(actualDay.strftime("%m")), actualDay.strftime("%d"), dishesperDay, True)
        # else:
        #     days[actualDay.day] = Day(year, int(actualDay.strftime("%m")), actualDay.strftime("%d"), dishesperDay, False)
        # if actualDay == datetime.now().date():
        #     days[actualDay.day].isToday = True
 
        if dishesperDay.count() == 0:
            days[actualDay.day] = dt.strftime(actualDay, '%Y-%m-%d')
        else:
            days[actualDay.day] = dishesperDay
            for dish in dishesperDay:
                if Dish.query.filter_by(dish_id=dish.dish_id).count() > 0:
                    dishes[dish.dish_id] = Dish.query.filter_by(dish_id=dish.dish_id).first().name
    if message:
        flash(message)
    output = render_template('displayWeek.html', date_title=date_title, linkCreateDish=url_for('formCreateDish'), linkchooseDish=url_for('formChooseDish'), nextWeek=(choosenDate+timedelta(days=7)).strftime("%Y-%m-%d"), lastWeek=(choosenDate+timedelta(days=-7)).strftime("%Y-%m-%d"), choosenDatum=monday, year=year, monthName=month, monthNames=monthNames, monthNumbers=monthNumbers, week=week, weekdays=weekdays, month=monday.month-1, days=days, dishes=dishes)
    return output


@app.route("/dishes")
@login_required
def listDishes():
    return render_template('dishes.html',
                           dishes=Dish.query.filter_by(user_id=current_user.id),
                           title="Show Dishes")


@app.route("/dish/<int:dish_id>")
@login_required
def showDish(dish_id):
    if type(dish_id) is int:
        dish = Dish.query.filter_by(dish_id=dish_id).first_or_404()
        # tag_for_dish = Tags.query.filter_by(dish_id=dish_id)
        
        if dish.note:
            dish.note = dish.note.replace('\n', '<br>')
        else:
            dish.note = ''
        # for tag in tag_for_dish:
        #     print(tag)
        # ingredientsAll = Ingredient()
        ingredients = Ingredient.query.filter_by(dish_id=dish_id)
        print(type(ingredients))
        return render_template('dish.html',
                           dish=dish,
                           title="Show Dish", ingredients=ingredients, ingredientsCount=ingredients.count())
        # return render_template('dish.html', dish=dish, ingredients=ingredients, ingredientsCount=len(ingredients))
    else:
        returnText = "Detailansicht eines Gerichts: Fehler"


@app.route("/createDish", methods=["POST","GET"])
@login_required
def createDish():
    params = {}
    if request:
        name = request.form.get('name', '')
        note = request.form.get('note', '')
        tags = request.form.getlist('tag')
        # ingredients = request.args.get('ingredients', '')
        countCooked = 0
        # Noch ist hier eine statische user_id, muss mit der aktuellen ersetzt werden.
        user_id = 1

        if name:
            new_dish = Dish(name=name,
                            note=note,
                            countCooked=0,
                            user_id=current_user.id,
                            created=dt.now())
            # Tags dem Dish-Objekt hinzufügen
            for tag_name in tags:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    new_dish.tags.append(tag)
            db.session.add(new_dish)  # Adds new Dish record to database
            db.session.commit()  # Commits all changes
            dish_id = Dish.query.filter_by(name=name).first().dish_id
            return redirect(url_for('showDish',dish_id=dish_id))
            # return render_template('dishes.html',
            #                     dishes=Dish.query.all(),
            #                     title="Show Dishes")


@app.route("/chooseDish", methods=["POST", "GET"])
@login_required
def formChooseDish():
    choosenDate = request.args.get('choosen_date')
    listDishes = Dish.query.filter_by(user_id=current_user.id)
    return render_template('formChooseDish.html', dishes=listDishes, date=choosenDate)


@app.route("/assignDish", methods=["POST", "GET"])
@login_required
def assignDish():
    dish_id = int(request.args.get('dish_id', ''))
    choosen_date = dt.strptime(request.args.get('choosen_date', ''), '%Y-%m-%d').date()
    # choosen_date = dt(2019, 8, 22, 10, 10, 10)
    if dish_id and choosen_date:
        new_day = Days(date=choosen_date,
                        date_as_string=dt.strftime(choosen_date, '%Y-%m-%d'),
                            dish_id=dish_id,
                            user_id=current_user.id)
        
        db.session.add(new_day)  # Adds new Dish record to database
        db.session.commit()  # Commits all changes

        return redirect(url_for('displayWeek',date=choosen_date))
    else:
        return "0"


@app.route("/removeDish", methods=["POST", "GET"])
@login_required
def removeDish():
    dish_id = int(request.args.get('dish_id', ''))
    choosen_date = dt.strptime(request.args.get('choosen_date', ''), '%Y-%m-%d').date()
    if dish_id and choosen_date:
        dish_at_day = Days.query.filter_by(date=choosen_date,dish_id=dish_id).first()
        db.session.delete(dish_at_day)
        db.session.commit()
        return redirect(url_for('displayWeek',date=choosen_date))
    else:
        return redirect(url_for('displayWeek',date=choosen_date))



@app.route("/formCreateDish")
@login_required
def formCreateDish():
    allTags = Tag.query.all()
    countTags = len(allTags)
    return render_template('formCreateDish.html', tags=allTags, countTags=countTags)


@app.route("/formEditDish", methods=["GET"])
@login_required
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
    dish = Dish.query.filter_by(dish_id=dish_id).first_or_404()
    
    # Umwandlung von html-Zeilenbrüche in Zeilenbrüche
    if dish.note:
        dish.note = dish.note.replace('<br />', '\n')
    else:
        dish.note = ''
    
    # dish['tags'] = tag_for_dish
    

    # Allgemeine Tags laden
    allTags = Tag.query.filter_by(user_id=current_user.id)
    countTags = allTags.count()

    # Zutaten für das Gericht laden
    ingredients = Ingredient.query.filter_by(dish_id=dish_id)

    # Alle Namen und Einheiten der Zutaten laden
    suggestions = Ingredient.query.all()

    # Tags selektieren
    for index in range(allTags.count()):
        for tag2 in dish.tags:
            if allTags[index].tag_id == tag2.tag_id:
                allTags[index].selected = " selected"

    # Template füllen und zurückgeben
    return render_template('formEditDish.html', allTags=allTags, countTags=countTags, dish=dish, ingredients=ingredients, ingredientsCount=ingredients.count(), suggestions=suggestions)


@app.route("/editDish", methods=["POST"])
@login_required
def editDish():
    params = {}
    if request:
        # Parameter holen.
        params["dish_id"] = request.form.get('dish_id', '')
        params["name"] = request.form.get('name', '')
        params["note"] = request.form.get('note', '')
        params["countCooked"] = "0"
        params["tags"] = request.form.getlist('tags')
        
        
        # Folgendes checkt, ob ein Tag vorhanden ist. Wenn nicht, würde er neu angelegt werden.
        # Ist aber überflüssig, da in dem Formular zum editieren eines Gerichts keine neuen Tags eingegeben werden können.
        # tags_list = []
        # # Alle Tags durchgehen und eventuell neue anlegen
        # for tag_name_request in params["tags"]:
        #     tag_id = Tag.query.filter_by(name=tag_name_request,user_id=0).first().tag_id
        #     # Wenn tag_id nicht geholt werden konnte, muss der Tag erstellt werden
        #     if not tag_id:
        #         new_tag = Tag(name=name,
        #                     user_id=0)
        #         db.session.add(new_tag)  # Adds new Dish record to database
        #         db.session.commit()  # Commits all changes
        #     tags_list.append(tag_id)
        
        # Dish-Objekt holen
        dish = Dish.query.filter_by(dish_id=params["dish_id"]).first()

        # Mögliche Änderungen zuweisen
        dish.name = params['name']
        dish.countCooked = int(params['countCooked'])
        dish.note = params['note']
        
        # 1. Löschen der alten zugewiesenen Tags
        # 2. Die übergebenen Tags dem Gericht zuweisen
        dish.tags = []
        for tag_name in params['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            dish.tags.append(tag)

        
        # Änderungen committen       
        db.session.commit()

        
        return redirect(url_for('showDish',dish_id=params["dish_id"]))


@app.route("/deleteDish", methods=["POST", "GET"])
@login_required
def deleteDish():
    if request:
        dish = Dish.query.filter_by(dish_id=request.form.get('dish_id', '')).delete()
        db.session.commit()
        
        return redirect(url_for('listDishes'))
    else:
        return "Fehler! <br /><a href\"" + url_for('listDishes') + "\">Liste</a>"


@app.route("/createIngredient", methods=["POST", "GET"])
def createIngredient():
    params = {}
    if request:
        params["dish_id"] = request.form.get('dish_id', '')
        params["name"] = request.form.get('name', '')
        params["amount"] = request.form.get('amount', '')
        params["unit"] = request.form.get('unit', '')
        Dish.query.filter_by(dish_id=params["dish_id"]).first_or_404()       
        if params['name'] == '' or int(params['amount']) == 0 or params['unit'] == '':
            return redirect(url_for('formEditDish', dish_id=params["dish_id"]))
        ing = Ingredient(name = params["name"],
                        amount = params["amount"],
                        unit = params["unit"],
                        dish_id = params["dish_id"],
                        user_id = current_user.id)
        db.session.add(ing)  # Adds new Ingredient record to database
        db.session.commit()  # Commits all changes


        return redirect(url_for('formEditDish', dish_id=params["dish_id"]))
    else:
        return "Fehler"


@app.route("/deleteIngredient", methods=["POST", "GET"])
@login_required
def deleteIngredient():
    if request:
        ing_id = int(request.args.get('ing_id', ''))
        dish_id = int(request.args.get('dish_id', ''))
        if ing_id == '' or dish_id == '':
            return redirect(url_for('formEditDish', dish_id=dish_id))

        ing = Ingredient.query.filter_by(id=ing_id).first_or_404()
        db.session.delete(ing)
        db.session.commit()
        
        return redirect(url_for('formEditDish', dish_id=dish_id))
    else:
        return "Fehler! <br /><a href\"" + url_for('getTags') + "\">Liste</a>"




@app.route("/tags", methods=["GET"])
@login_required
def getTags():
    has_message = False
    if request:
        if request.args.get('msg', ''):
            has_message = request.args.get('msg', '')
        # return redirect(url_for('listDishes'))
    else:
        has_message = False
        return "Fehler! <br /><a href\"" + url_for('listDishes') + "\">Liste</a>"
    allTags = Tag.query.filter_by(user_id=current_user.id)
    # if len(allTags) > 0:
    #     for tag in allTags:
    #         print(tag)
    
    return render_template('tags.html', tags=allTags, has_message=has_message)


@app.route("/createTag", methods=["POST"])
@login_required
def createTag():
    params = {}
    if request:
        params["name"] = request.form.get('name', '')
        
        if params['name'] == '':
            return redirect(url_for('getTags'))
        tag = Tag(name = params["name"],
                        user_id = current_user.id)
        
        db.session.add(tag)  # Adds new Ingredient record to database
        db.session.commit()  # Commits all changes


        return redirect(url_for('getTags'))
    else:
        return "Fehler"

@app.route("/deleteTag", methods=["POST", "GET"])
@login_required
def deleteTag():
    if request:
        tag_id = int(request.args.get('tag_id', ''))
        tag = Tag.query.filter_by(tag_id=tag_id).first_or_404()
        dishes = Dish.query.with_parent(tag)
        new_tag_list = []
        for dish in dishes:
            for index in range(len(dish.tags)):
                # print("{0}-{1}".format(dish.tags[index].tag_id, tag_id))
                if not dish.tags[index].tag_id == tag_id:
                    new_tag_list.append(dish.tags[index])
            dish.tags = new_tag_list
            new_tag_list = []
        db.session.delete(tag)
        db.session.commit()
        
        return redirect(url_for('getTags'))
    else:
        return "Fehler! <br /><a href\"" + url_for('getTags') + "\">Liste</a>"


@app.route("/addToWunderlist", methods=["POST", "GET"])
@login_required
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
    from datetime import date, timedelta, datetime
    from .customFunctions import getMonday, addTodoListToWunderlist
    
    import operator
    try:
        choosenDate = datetime.strptime(request.args.get('date', ''), "%Y-%m-%d").date()
    except:
        choosenDate = date.today()
    monday = getMonday(choosenDate)
    day = monday.day
    year = monday.strftime("%Y")
    # week = [(monday+timedelta(days=0)).day, (monday+timedelta(days=1)).day, (monday+timedelta(days=2)).day, (monday+timedelta(days=3)).day, (monday+timedelta(days=4)).day, (monday+timedelta(days=5)).day, (monday+timedelta(days=6)).day]
    # weekdays = {(monday+timedelta(days=0)).day:'Montag', (monday+timedelta(days=1)).day:'Dienstag', (monday+timedelta(days=2)).day:'Mittwoch', (monday+timedelta(days=3)).day:'Donnerstag', (monday+timedelta(days=4)).day:'Freitag', (monday+timedelta(days=5)).day:'Samstag', (monday+timedelta(days=6)).day:'Sonntag'}
    
    dishes_for_wunderlist = {}
    

    ingredients_for_wunderlist = []
    ingredients = {}
    ingredients_obj = []
    for day in range(0,7):
        actualDay = monday+timedelta(days=day)
        dishesperDay = Days.query.filter_by(date=actualDay,user_id=current_user.id)
        for dish in dishesperDay:
            # print(dish)
            dish_ingredients = Dish.query.filter_by(dish_id=dish.dish_id).first().ingredients
            # dish_ingredients = ingredientsObject.list(dish['dish_id'])
            for ing in dish_ingredients:
                
                if not ing.amount:
                    continue
                amount = ing.amount
                if amount % 1 == 0:
                    amount = int(amount)
                ing.amount = amount
                element_index = next((index for (index, d) in enumerate(ingredients_obj) if d.name == ing.name), None)
                if element_index:
                    # print("Gefunden: " + ing.name)
                    ingredients_obj[element_index].amount += amount
                else:
                    ingredients_obj.append(ing)

    # Zutaten sortieren
    
    # ingredients_obj.sort(key=operator.itemgetter('name'))

    for ing in ingredients_obj:
        if ing.unit + " " + ing.name in ingredients:
            ingredients[ing.unit + " " + ing.name] += ing.amount
        else:
            ingredients[ing.unit + " " + ing.name] = ing.amount

    for key, value in ingredients.items():
        if not addTodoListToWunderlist("{0}{1}".format(value, key)) == 201:
            return "Error!"
    # print(ingredients['g Reis'])
    # Test, der eine einzelne Todo erstellt
    # if not addTodoListToWunderlist("2.0 Stück Chilischote") == 201:
    #          return "Error!"

    return redirect(url_for('displayWeek', date=choosenDate, message='Zutaten wurden zur Wunderlist hinzugefügt'))



@app.route('/')
def home_page():
    return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>{%trans%}Home page{%endtrans%}</h2>
                <p><a href={{ url_for('user.register') }}>{%trans%}Register{%endtrans%}</a></p>
                <p><a href={{ url_for('user.login') }}>{%trans%}Sign in{%endtrans%}</a></p>
                <p><a href={{ url_for('home_page') }}>{%trans%}Home Page{%endtrans%}</a> (accessible to anyone)</p>
                
                <p><a href={{ url_for('admin_page') }}>{%trans%}Admin Page{%endtrans%}</a> (role_required: admin@example.com / Password1')</p>
                <p><a href={{ url_for('user.logout') }}>{%trans%}Sign out{%endtrans%}</a></p>
            {% endblock %}
            """)

# Routing for Multi-User
@app.route('/admin')
@login_required
def admin_page():
    return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>{%trans%}Admin Page{%endtrans%}</h2>
                <p><a href={{ url_for('user.register') }}>{%trans%}Register{%endtrans%}</a></p>
                <p><a href={{ url_for('user.login') }}>{%trans%}Sign in{%endtrans%}</a></p>
                <p><a href={{ url_for('home_page') }}>{%trans%}Home Page{%endtrans%}</a> (accessible to anyone)</p>
                <p><a href={{ url_for('member_page') }}>{%trans%}Member Page{%endtrans%}</a> (login_required: member@example.com / Password1)</p>
                <p><a href={{ url_for('admin_page') }}>{%trans%}Admin Page{%endtrans%}</a> (role_required: admin@example.com / Password1')</p>
                <p><a href={{ url_for('user.logout') }}>{%trans%}Sign out{%endtrans%}</a></p>
            {% endblock %}
            """)