from flask import Flask, render_template, request, flash, redirect, get_flashed_messages, url_for
import psycopg2
from psycopg2.extras import NamedTupleCursor
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import validators
import requests

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

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
        host = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        if validators.url(url) and len(url) <= 255:
            try:
                with conn:
                    with conn.cursor() as curs:
                        query = "(SELECT * FROM urls WHERE name = %s)"
                        curs.execute(query, (host,))
                        row = curs.fetchone()
                        if not row:
                            curs.execute('INSERT INTO urls (name) VALUES (%s)', (host,))
                            flash('Страница успешно добавлена', 'success')
                        else:
                            flash('Страница уже существует', 'warning')
                        curs.execute('SELECT id FROM urls WHERE name=%s', (host,))
                        id = curs.fetchone()[0]
                        return redirect(url_for('show_site', id=id))
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            flash('Некорректный URL', 'error')
            return redirect(url_for('index'))

    try:
        with conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                query = "SELECT u.id, u.name, ch.created_at, ch.status_code " \
                        "FROM urls AS u " \
                        "LEFT JOIN (" \
                        "   SELECT u_c.url_id, u_c.created_at, u_c.status_code " \
                        "   FROM url_checks AS u_c " \
                        "   JOIN (" \
                        "       SELECT url_id, MAX(created_at) AS created_at " \
                        "       FROM url_checks" \
                        "       GROUP BY url_id" \
                        "   ) AS l_u_c ON u_c.url_id = l_u_c.url_id AND u_c.created_at = l_u_c.created_at" \
                        ") AS ch ON u.id = ch.url_id"
                curs.execute(query)
                urls = curs.fetchall()
    except Exception as e:
        print(f"An error occurred: {e}")

    return render_template('sites.html', urls=urls, messages=messages)


@app.route('/urls/<id>')
def show_site(id):
    messages = get_flashed_messages(with_categories=True)
    try:
        with conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
                url = curs.fetchone()
                curs.execute('SELECT * FROM url_checks WHERE url_id=%s', (id,))
                checks = curs.fetchall()
    except Exception as e:
        print(f"An error occurred: {e}")

    return render_template('site_info.html', url=url, checks=checks, messages=messages)


@app.route('/urls/<id>/checks', methods=['POST'])
def start_check(id):
    try:
        with conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
                query = "SELECT name FROM urls WHERE id=%s"
                curs.execute(query, (id,))
                url = curs.fetchone()[0]
                r = requests.get(url, timeout=1)
                r.raise_for_status()
                status_code = r.status_code
                query = "INSERT INTO url_checks (url_id, status_code) VALUES (%s, %s)"
                curs.execute(query, (id, status_code))
                flash('Страница успешно проверена', 'success')
                return redirect(url_for('show_site', id=id))
    except Exception as e:
        print(f"An error occurred: {e}")
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('show_site', id=id))
