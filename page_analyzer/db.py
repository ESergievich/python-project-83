import os
import psycopg2
from psycopg2.extras import NamedTupleCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

URL_PARAMS = {
    'name': "(SELECT * FROM urls WHERE name = %s)",
    'id': "SELECT * FROM urls WHERE id=%s"
}

URL_CHECKS_PARAMS = {
    'url_id': "SELECT * FROM url_checks WHERE url_id=%s"
}


def get_url_by_param(param, value):
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            query = URL_PARAMS[param]
            curs.execute(query, (value,))
            url = curs.fetchone()
    return url


def insert_url_in_urls(name):
    with conn:
        with conn.cursor() as curs:
            query = "INSERT INTO urls (name) VALUES (%s)"
            curs.execute(query, (name,))


def get_all_urls_with_max_cr_at():
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
    return urls


def get_url_checks_by_param(param, value):
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            query = URL_CHECKS_PARAMS[param]
            curs.execute(query, (value,))
            url_checks = curs.fetchall()
    return url_checks


def insert_data_in_url_checks(data):
    with conn:
        with conn.cursor() as curs:
            query = "INSERT INTO url_checks (url_id, status_code, h1, title, description) VALUES (%s, %s, %s, %s, %s)"
            curs.execute(query, (*data,))
