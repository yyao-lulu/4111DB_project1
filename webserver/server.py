#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "yy2827"
DB_PASSWORD = "3lje529a"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


ttest = """
        drop table if exists vtest cascade;

        create table vtest(
            user_name text primary key,
            full_name text not null,
            photo_link text,
            fb_account text
        );
        insert into vtest VALUES 
        ( 'christianromeroUP', 'Christian Romero', 'https://graph.facebook.com/v2.10/10205730053050604/picture?type=large', '10205730053050604'),
        ( 'Jeffrey-Kemper-1', 'Jeffrey Kemper',  'https://venmopics.appspot.com/u/v1/m/c50b130d-feca-4dac-8caa-0961294bdd36', ''),
        (  'Guo-Zhiqi', 'Guo Zhiqi', 'https://venmopics.appspot.com/u/v1/n/0074e266-68ff-461b-96b5-9bb19661ec06', ''),
        (  'MeganResnick', 'Megan Resnick',  'https://venmopics.appspot.com/u/v3/n/e9692dd2-5a9f-4b1d-99b8-b074144b82ee', ''),
        (  'NoahGershwin', 'Noah Gershwin', 'https://venmopics.appspot.com/u/v1/m/09298cd9-cfb7-46b2-a364-cf59d505c0a4', ''),
        ( 'Marisa-Chambers', 'Marisa Chambers', 'https://graph.facebook.com/v2.10/10207315721424646/picture?type=large', '10207315721424646'),
        (  'elisadangelo', 'Elisa Dangelo', 'https://graph.facebook.com/v2.10/742587752539110/picture?type=large', '742587752539110'),
        ( 'anthonynguyen1006', 'Anthony Nguyen', 'https://venmopics.appspot.com/u/v2/m/f4d64bee-fcf6-4d50-932d-5f0d77875727', ''),
        (  'jjscarz', 'Julia Scarangella', 'https://venmopics.appspot.com/u/v1/m/d9ccd086-8cf3-4a1e-99ae-9bd12c1e67ee', ''),
        (  'Michael-Caguioa', 'Michael Caguioa',  'https://venmopics.appspot.com/u/v2/m/06b44f04-063a-4dc5-aa9d-410397fd023f', ''),
        ( 'Brian-Du-3', 'Brian Du', 'https://venmopics.appspot.com/u/v1/n/cba5b23a-940d-4d2f-8df0-631d9a96f09e', ''),
        ( 'Andrew-Kwon-8', 'Andrew Kwon', 'https://venmopics.appspot.com/u/v1/n/c66f063d-5e59-4ba3-a766-0e673323326d', '');
        """

engine.execute(ttest)


engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

##################################################################################
@app.route('/', methods=['GET','POST'])
def index():
  if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        if data['option'] == 'user_by_name':
            cursor = g.conn.execute("SELECT user_name FROM venmo_users WHERE user_name = %s", data['content'])
            user = cursor.fetchone()
            if user is None:
                return render_template('index.html', error="No such user")
            return redirect(url_for('read_user', id=data['content']))
        elif data['option'] == 'trx_by_date':
            cursor = g.conn.execute("SELECT payment_id FROM transa_transf WHERE created_time = %s", data['content'])
            corporation = cursor.fetchone()
            if corporation is None:
                return render_template('index.html', error="No such transaction")
            return redirect(url_for('read_trx', id=data['content']))
        else:
            return render_template('index.html', error="Invalid option")
  return render_template("index.html", error=None)

@app.route('/users')
def users():
  cursor = g.conn.execute("SELECT * FROM vtest")
  users = cursor.fetchall()
  return render_template('users.html', users=users)

@app.route('/user/<id>')
def read_user(id):
  cursor = g.conn.execute("SELECT * FROM vtest WHERE user_name = %s", id)
  user = cursor.fetchone()
  return render_template('/user.html', user=user)

@app.route('/trx/<id>')
def read_trx(id):
  cursor = g.conn.execute("SELECT * FROM transa_transf WHERE created_time = %s", id)
  trx = cursor.fetchall()
  return render_template('/trx.html', trx=trx)


@app.route('/another')
def another():
  return render_template("anotherfile.html")


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
