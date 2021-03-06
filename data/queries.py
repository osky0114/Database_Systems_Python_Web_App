from flask import request

__author__ = 'RR1'

import bcrypt
import easypg

def compare_unpw(username, pw_challenge):
    """
    Compares the password given to the hashed version in the database
    :param username: The username for which to authenticate against.
    :param pw_challenge: The password to challenge authentication.
    :return:
    """

    with easypg.cursor() as cur:
        cur.execute('''
            SELECT password
            FROM users
            WHERE username = %s
        ''', (username, ))

        # See this page for more information http://www.tutorialspoint.com/python/python_tuples.htm
        user_info = cur.fetchone()
        if user_info is None:
            return False
        else:
            #for row in user_info:
             #   print row
            pw = user_info[0]

            if bcrypt.hashpw(pw_challenge, pw) == pw:
                return True
            else:
                return False


def encrypt_password(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())


def add_user(cur, username, password, email):
    """
    Add the user to the database.
    :param username: Username to add.
    :param password: Password to add.
    :param email: Email address to add.
    :param dob: Date of Birth to add.
    :return:
    """
    cur.execute('''
        INSERT INTO users (username, password, email, dob, user_role, start_date, last_login, end_date)
        VALUES (%s, %s, %s, current_date, 1 , current_date, current_timestamp, null);
        COMMIT;
    ''', (username, encrypt_password(password), email))
    return None


def get_all_user_list(cur, page, user_id):
    """
    Get all lists user_id has stored in database .
    :param cur: the database cursor
    :return: a list of dictionaries of article IDs and titles
    """

    cur.execute('''
        SELECT list_title
        FROM lists
        WHERE created_by = user_id %s
    ''', ((page - 1) * 50,))
    user_list = []
    for list_title in cur:
         user_list.append({'lists_tile': list_title })
    return user_list


def search_titles(cur, query):
    cur.execute('''
        SELECT title_id, title, edition_id
        FROM titles
        JOIN editions USING (title_id)
        WHERE title @@ plainto_tsquery(%s)
        ORDER BY title DESC, title
    ''', (query, ))

    result = []
    for title_id, title, edition_id in cur:
        result.append({'id': title_id, 'title': title, 'edition_id': edition_id})

    return result


def search_authors(cur, query):
    cur.execute('''
        SELECT author_id, author_name
        FROM authors
        WHERE author_name @@ plainto_tsquery(%s)
        ORDER BY author_name DESC, author_name
    ''', (query, ))

    result = []
    for author_id, author_name in cur:
        result.append({'id': author_id, 'author_name': author_name})

    return result


def search_categories(cur, query):
    cur.execute('''
        SELECT category_id, cat_description
        FROM categories
        WHERE cat_description @@ plainto_tsquery(%s)
        ORDER BY cat_description DESC, cat_description
    ''', (query, ))

    result = []
    for category_id, cat_description in cur:
        result.append({'id': category_id, 'cat_description': cat_description})

    return result


def search_users(cur, query):
    cur.execute('''
        SELECT user_id, username
        FROM users
        WHERE username @@ plainto_tsquery(%s)
        ORDER BY username DESC, username
    ''', (query, ))

    result = []
    for user_id, username in cur:
        result.append({'id': user_id, 'username': username})

    return result

def get_user_id(cur, u_name):
    cur.execute('''
                SELECT user_id
                FROM   users
                WHERE  username = %s
                ''', (u_name,)
                )
    f = cur.fetchone()
    uid = int(f[0])
    return uid

def get_author_books(cur, query):
    cur.execute('''
        SELECT authors.author_id, authors.author_name, COALESCE(ISBN, 'Not Available') AS ISBN,
        COALESCE(edition_name, 'Not Available') AS edition_name, COALESCE(page_count, 0) AS page_count,
        COALESCE(title, 'Not Available') AS title, COALESCE(pub_name, 'Not Available') AS pub_name, pub_date
        FROM authors
        JOIN editions_authors ON (editions_authors.author_id = authors.author_id)
        JOIN editions ON (editions.edition_id = editions_authors.edition_id)
        JOIN titles ON (titles.title_id = editions.title_id)
        JOIN editions_publishers ON (editions_publishers.edition_id = editions.edition_id)
        JOIN publishers ON (publishers.publisher_id = editions_publishers.publisher_id)
        WHERE authors.author_id = %s;
    ''', (query, ))

    result = []
    for author_id, author_name, ISBN, edition_name, page_count, title, pub_name, pub_date in cur:
        result.append({'author_id': author_id,
                       'author_name': author_name,
                       'ISBN': ISBN,
                       'edition_name': edition_name,
                       'page_count': page_count,
                       'title': title,
                       'pub_name': pub_name,
                       'pub_date': pub_date})
    return result