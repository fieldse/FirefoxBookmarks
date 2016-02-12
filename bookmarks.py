#!/usr/bin/env python3
"""	A simple python module to list the Firefox bookmarks on
        the commandline and let user choose.
        Opens in browser
"""
import os,sys
import sqlite3
import subprocess

USR_HOME_DIR = os.path.expanduser('~')
FIREFOX_DIR = os.path.join(USR_HOME_DIR, '.mozilla/firefox')
BROWSER = '/usr/bin/firefox'
# this may change with operating system

def get_local_firefox_dir():
    if not os.path.isdir(FIREFOX_DIR):
        print('Firefox directory not found.')
        sys.exit()
    files = os.listdir(FIREFOX_DIR)
    for f in files:
        if f.endswith('.default'):
            my_ff_dir = os.path.join(FIREFOX_DIR, f)
    return my_ff_dir 


def open_sql_connection(MY_FIREFOX_DIR):
    db_file = os.path.join(MY_FIREFOX_DIR, 'places.sqlite')
    if not os.path.isfile(db_file):
        print('Bookmarks db file %s not found.' % db_file)
        sys.exit()
    try:
        conn = sqlite3.connect(db_file)
        print('Connected to bookmarks database')
        return conn
    except:
        print('Unable to connect to database')
        sys.exit()

def query_db(conn):
    c = conn.cursor()
    q = '''select b.title, url from moz_bookmarks as b
        join moz_places as p
        where (b.parent = 2 and b.fk = p.id)
        order by b.position
        '''
    result = c.execute(q)
    data = c.fetchall()
    print(len(data), 'results returned.')
    return data

def make_list(data):
    if not len(data) > 0:
        print('No results.')
        sys.exit()
    bookmarks = []
    for i,row in enumerate(data):
        name,url = row
        bookmarks.append( {'number':i, 'name':name, 'url':url } )

    return bookmarks

def select_menu(bookmarks):
    len_items = len(bookmarks)

    for item in bookmarks:
        number = item['number']
        name = item['name']
        print('[%d] %s' % (number,name))

    print('Choose one')
    while True:
        try:
            selection = input(' > ')
            if not selection.isnumeric():
                print('Please choose a number.')
                continue
            selection = int(selection)
            if not selection < len_items:
                print('Choose a number in range.')
                continue
            else:
                url = bookmarks[selection]['url']
                break
        except KeyboardInterrupt:
            sys.exit()
        else:
            return url 

def spawn_browser(url):
    cmd = [BROWSER, '--new-tab', url]
    print(url)
    print('Opening \'%s\' in browser' % url)
    subprocess.call(cmd, stdout=subprocess.PIPE)

def main():
    MY_FIREFOX_DIR = get_local_firefox_dir()
    conn = open_sql_connection(MY_FIREFOX_DIR)
    data = query_db(conn)
    bookmarks = make_list(data)
    url = select_menu(bookmarks)
    spawn_browser(url)

if __name__ == '__main__':
    main()
