import sqlite3
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from .models import Programator,Denik,Tags,User,Kategorie,Jazyk
from flask import Blueprint
from flask_login import login_required, current_user
from .config import UI,Palette, Filter
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    db.create_all()
    languages = Jazyk.query.order_by(Jazyk.id).all()
    for language in languages:
        Filter.language_dict[int(language.id)] = "on"

    tags = Tags.query.order_by(Tags.id).all()
    for tag in tags:
        Filter.tag_dict[int(tag.id)] = "on"
    Filter.tag_dict[0] = "on"
    UI.active = "home"
    return render_template('index.html', user = current_user,active=UI.active,palette=Palette)

@main.route('/language/')
@login_required
def showLanguageTable():
    languages = Jazyk.query.order_by(Jazyk.id).all()
    UI.active = "language"
    return render_template('jazyky.html', user = current_user,active=UI.active,languages=languages,palette=Palette)

@main.route('/programmer/')
@login_required
def showTableProgrammer():
    UI.active = "programmer"
    programmers = Programator.query.order_by(Programator.id).all()
    return render_template('programatori.html', user = current_user,active=UI.active,programmers=programmers,palette=Palette)

@main.route('/cat/')
@login_required
def showCatTable():
    tags = Tags.query.order_by(Tags.id).all()
    UI.active = "cat"
    return render_template('kategorie.html', user = current_user,active=UI.active, tags=tags,palette=Palette)

@main.route('/zaznamy/<int:serazeni>/', methods=['POST', 'GET'])
@login_required
def zaznamy(serazeni):
    cats = Kategorie.query.order_by(Kategorie.id).all()
    languages = Jazyk.query.order_by(Jazyk.id).all()
    records = db.session.query(Denik).order_by(Denik.date).all()
    programmers = Programator.query.order_by(Programator.id).all()
    tags = Tags.query.order_by(Tags.id).all()
    if(serazeni == 1):
        #datum od nejdříve
        records = db.session.query(Denik).order_by(Denik.date)
    if(serazeni == 2):
        #datum od nejpozději
        records = db.session.query(Denik).order_by(Denik.date.desc())
    if(serazeni == 3):
        #čas od nejvíce
        records = db.session.query(Denik).order_by(Denik.time_spent.desc())
    if(serazeni == 4):
        #čas od nejméně
        records = db.session.query(Denik).order_by(Denik.time_spent)
    if(serazeni == 5):
        #hodnocení od nejvíce
        records = db.session.query(Denik).order_by(Denik.hodnoceni.desc())
    if(serazeni == 6):
        #hodnocení od nejvíce
        records = db.session.query(Denik).order_by(Denik.hodnoceni)
    if(serazeni == 7):
        #programovací jazyk
        records = db.session.query(Denik).order_by(Denik.jazyk_id)
    if(serazeni == 8):
        #programovací jazyk naopak (nemáme v provozu)
        records = Denik.query.order_by(Denik.jazyk_id).all()

    for r in records:
        #před porovnáváním hodnoty stringů se musí dostat do proměnných nějaká hodnota
        Filter.date_from = r.date
        Filter.date_to = r.date
        Filter.time_from = r.time_spent
        Filter.time_to = r.time_spent
        Filter.hodnoceni_to = r.hodnoceni
        Filter.hodnoceni_from = r.hodnoceni

    for r in records:
        if(str(Filter.date_to) < str(r.date)):
            Filter.date_to = r.date
        if(str(Filter.date_from) > str(r.date)):
            Filter.date_from = r.date
        if(int(Filter.time_to) < int(r.time_spent)):
            Filter.time_to = r.time_spent
        if(int(Filter.time_from) > int(r.time_spent)):
            Filter.time_from = r.time_spent
        if(int(Filter.hodnoceni_from) > int(r.hodnoceni)):
            Filter.hodnoceni_from = r.hodnoceni
        if(int(Filter.hodnoceni_to) < int(r.hodnoceni)):
            Filter.hodnoceni_to = r.hodnoceni


    if request.method == 'POST':
        for language in languages:
            try:
                #try protoze pokud neni oznacen, tak by to melo hodit exception
                Filter.language_dict[int(language.id)] = request.form[str(language.name)]
            except:
                Filter.language_dict[int(language.id)] = 0

        for tag in tags:
            try:
                #try protoze pokud neni oznacen, tak by to melo hodit exception
                Filter.tag_dict[int(tag.id)] = request.form[str(tag.name)]
            except:
                Filter.tag_dict[int(tag.id)] = 0
        try:
            Filter.tag_dict[0] = request.form[str(0)]
        except:
            Filter.tag_dict[0] = int(0)

        Filter.time_from = request.form['time_from']
        Filter.time_to = request.form['time_to']
        Filter.date_from = request.form['date_from']
        Filter.date_to = request.form['date_to']
        Filter.hodnoceni_from = request.form['hodnoceni_from']
        Filter.hodnoceni_to = request.form['hodnoceni_to']
        Filter.hodnoceni_from = request.form['hodnoceni_from']
        Filter.hodnoceni_to = request.form['hodnoceni_to']
        Filter.name = request.form['name']

    #zde se provádí filtrace
    if (int(Filter.name) != int(0)):
        records = records.filter(Denik.name == Filter.name)
    records = records.filter(Denik.date <= Filter.date_to).filter(Denik.date >= Filter.date_from)
    records = records.filter(Denik.time_spent >= Filter.time_from).filter(Denik.time_spent <= Filter.time_to)
    records = records.filter(Denik.hodnoceni <= Filter.hodnoceni_to).filter(Denik.hodnoceni >= Filter.hodnoceni_from)
    if(not Filter.tag_dict[0]):
        for record in records:
            has = False
            for cat in cats:
                if (int(record.id) == int(cat.owned_id)):
                    has = True
            if (has == False):
                records = records.filter(int(Denik.id) !=  int(record.id))
    for language in languages:
        if(not Filter.language_dict[int(language.id)]):
            records = records.filter(Denik.jazyk_id !=  language.id)
    for tag in tags:
        if(not Filter.tag_dict[int(tag.id)]):
            for record in records:
                has = False
                for cat in cats:
                    if (int(cat.owned_id) == int(record.id) and int(cat.type_id) == int(tag.id)):
                        has = True
                if (has == True):
                    records = records.filter(Denik.id != record.id)
    UI.active = "records"
    return render_template('zaznamy.html', user = current_user,active=UI.active, records=records, languages=languages, programmers=programmers, tags=tags, cats=cats, \
    filtered_languages=Filter.language_dict, filtered_tags=Filter.tag_dict, min_date=Filter.date_from, max_date=Filter.date_to, min_time=Filter.time_from, max_time=Filter. \
    time_to, max_hod=Filter.hodnoceni_to, min_hod=Filter.hodnoceni_from, sel_name=int(Filter.name), serazeni=serazeni,palette=Palette)


@main.route('/zaznamy/set-serazeni/', methods=['POST', 'GET'])
@login_required
def setSerazeniZaznamy():
    serazeni = request.form['serazeni']
    return redirect('/zaznamy/' + serazeni)
@main.route('/zaznamy/reset-filter', methods=['POST', 'GET'])
@login_required
def OGzaznamy():
    languages = Jazyk.query.order_by(Jazyk.id).all()
    for language in languages:
        Filter.language_dict[language.id] = "on"
    tags = Tags.query.order_by(Tags.id).all()
    for tag in tags:
        Filter.tag_dict[tag.id] = "on"
    records = Denik.query.order_by(Denik.date).all()
    Filter.name = 0
    for r in records:
        Filter.date_from = r.date
        Filter.date_to = r.date
        Filter.time_from = r.time_spent
        Filter.time_to = r.time_spent
        Filter.hodnoceni_to = r.hodnoceni
        Filter.hodnoceni_from = r.hodnoceni
    try:
        for r in records:
            if(Filter.date_to < r.date):
                Filter.date_to = r.date
            if(Filter.date_from > r.date):
                Filter.date_from = r.date
            if(Filter.time_to < r.time_spent):
                Filter.time_to = r.date
            if(Filter.time_from > r.time_spent):
                Filter.time_from = r.time_spent
            if(int(Filter.hodnoceni_from) > int(r.hodnoceni)):
                Filter.hodnoceni_from = r.hodnoceni
            if(int(Filter.hodnoceni_to) < int(r.hodnoceni)):
                Filter.hodnoceni_to = r.hodnoceni
    except:
        pass

    return redirect('/zaznamy/1/')