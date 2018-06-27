#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from integration import imports
from db import connect_db

# Create our little application :)
app = Flask(__name__)
# Read config
app.config.from_pyfile('config.py')


def get_db():
    """ Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/import', methods=['GET', 'POST'])
def import_history():
    num_added = None
    if request.method == 'POST':
        num_added = imports.firefox(get_db(), request.form['firefox_profile'])
    return render_template('import_history.html', num_added=num_added)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        session['logged_in'] = True
        flash('You were logged in')
        return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()