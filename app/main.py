import sqlite3
import json
from flask import Flask, render_template, request, redirect, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
from . import db, api_commits, api_users, api_sys
from .models import User, Commit, Note
from .config import Data

main = Blueprint('main', __name__)



def saveApi():
    Data.commit_num = 0
    for user in User.query.order_by(User.changes).all():
        user.lines_added = 0
        user.lines_removed = 0
        user.changes = 0
    data = api_users.text
    users_json = json.loads(data)
    for user in users_json:
        if not User.query.filter_by(userID=user['userID']).first():
            # add the new user to the database
            new_user = User(name=user['name'], surname=user['surname'], nick=user['nick'], userID=user['userID'])
            db.session.add(new_user)
            db.session.commit()
    data = api_commits.text   
    commits_json = json.loads(data)
    for commit in commits_json:
        Data.commit_num += 1
        db_commit = Commit.query.filter_by(commit_id=commit['commit_id']).first()
        if not db_commit:
            # add the new commit to the database
            new_commit = Commit(creator_id=commit['creator_id'], date=commit['date'], lines_added=commit['lines_added'], lines_removed=commit['lines_removed'], description=commit['description'], commit_id=commit['commit_id'])
            db.session.add(new_commit)
            db.session.commit()
        author = User.query.filter_by(userID=commit['creator_id']).first()
        if author:
            author.lines_added += commit['lines_added']
            author.lines_removed += commit['lines_removed']
            author.changes += commit['lines_added'] + commit['lines_removed']
            db.session.commit()
    data = api_sys.text
    sys_json = json.loads(data)
    for sys in sys_json:
        Data.cpu_load = sys['cpu_load']
        Data.ram_usage = sys['ram_usage']
        Data.disk_usage = sys['disk_usage']
        Data.boot_time = sys['boot_time']
        Data.platform = sys['platform']


@main.route('/')
def index():
    db.create_all()
    notes = Note.query.order_by(Note.id).all()
    return render_template('index.html', notes = notes)

@main.route('/stats/')
def stats():
    db.create_all()
    data = api_users.text
    parse_json = json.loads(data)
    saveApi()
    labels = []
    data = []
    i=0
    for user in User.query.order_by(User.changes.desc()).all():
        if i<5:
            fullname = "{name} {surname}"
            fullname.format(name= user.name, surname=user.surname)
            labels.append(fullname)
            labels.append(fullname)
            data.append(user.lines_added)
            data.append(user.lines_removed)
            i+=1
    bestProgrammer = User.query.order_by(User.changes.desc()).first()
    return render_template('stat.html',labels = labels, data = data, bestProgrammer=bestProgrammer, commit_num=Data.commit_num, api_users=parse_json, users=User.query.order_by(User.changes).all())