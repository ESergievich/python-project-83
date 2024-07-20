from flask import Flask, render_template, request, flash, redirect, get_flashed_messages, url_for
import os
from dotenv import load_dotenv
from .checks import validate_url, get_url_data
from .db import get_url_by_param, insert_url_in_urls, get_all_urls_with_max_cr_at, get_url_checks_by_param, \
    insert_data_in_url_checks

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls', methods=['GET', 'POST'])
def show_sites():
    messages = get_flashed_messages(with_categories=True)
    if request.method == 'POST':
        url = request.form.get('url')
        host = validate_url(url)
        if host:
            row = get_url_by_param('name', host)
            if not row:
                insert_url_in_urls(host)
                flash('Страница успешно добавлена', 'alert alert-success')
            else:
                flash('Страница уже существует', 'alert alert-primary')
            url_id = get_url_by_param('name', host).id
            return redirect(url_for('show_site', id=url_id))
        else:
            flash('Некорректный URL', 'alert alert-danger')
            return redirect(url_for('index'))

    urls = get_all_urls_with_max_cr_at()
    return render_template('sites.html', urls=urls, messages=messages)


@app.route('/urls/<id>')
def show_site(id):
    messages = get_flashed_messages(with_categories=True)
    url = get_url_by_param('id', id)
    url_checks = get_url_checks_by_param('url_id', id)
    return render_template('site_info.html', url=url, checks=url_checks, messages=messages)


@app.route('/urls/<id>/checks', methods=['POST'])
def start_check(id):
    try:
        url = get_url_by_param('id', id).name
        data = id, *get_url_data(url)
        insert_data_in_url_checks(data)
        flash('Страница успешно проверена', 'alert alert-success')
        return redirect(url_for('show_site', id=id))
    except Exception:
        flash('Произошла ошибка при проверке', 'alert alert-danger')
        return redirect(url_for('show_site', id=id))
