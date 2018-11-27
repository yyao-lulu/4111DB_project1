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
DB_USER = "bq2130"
DB_PASSWORD = "2v9c3q6j"


DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


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

            #user_card = cursor2.fetchone()
            #if user_card is None:
                #return render_template('index.html', error="No such user")
            #return redirect(url_for('read_card', id=data['content']))
        elif data['option'] == 'trx_by_date':
            cursor = g.conn.execute("SELECT payment_id FROM transa_transf WHERE created_time = %s", data['content'])
            transaction_by_date = cursor.fetchone()
            if transaction_by_date is None:
                return render_template('index.html', error="No such transaction")
            return redirect(url_for('read_trx', id=data['content']))
        elif data['option'] == 'risk_by_level':
            cursor = g.conn.execute("SELECT user_name FROM person_risk_result WHERE risk_level = %s", data['content'])
            user_risk = cursor.fetchone()
            if user_risk is None:
                return render_template('index.html', error="No such user")
            return redirect(url_for('read_risk', id=data['content']))
        else:
            return render_template('index.html', error="Invalid option")
  return render_template("index.html", error=None)

@app.route('/users')
def users():
  cursor = g.conn.execute("SELECT * FROM venmo_users")
  users = cursor.fetchall()
  return render_template('users.html', users=users)

@app.route('/trxs')
def trxs():
  cursor = g.conn.execute("SELECT * FROM transa_transf")
  trxs = cursor.fetchall()
  return render_template('trxs.html', trxs=trxs)

@app.route('/user/<id>')
def read_user(id):
  cursor = g.conn.execute("SELECT * FROM venmo_users WHERE user_name = %s", id)
  user = cursor.fetchone()
  cursor = g.conn.execute("SELECT * from bank_pay where user_name = %s", id)
  card = cursor.fetchall()
  cursor = g.conn.execute("SELECT * FROM person_risk_result WHERE user_name = %s", id)
  risk = cursor.fetchone()

  return render_template('/user.html', user=user, risk=risk, card = card)

@app.route('/risk/<id>')
def read_risk(id):
   cursor = g.conn.execute("SELECT * FROM person_risk_result WHERE risk_level = %s", id)
   users = cursor.fetchall()
   return render_template('/risk.html', users = users)

@app.route('/trx/<id>')
def read_trx(id):
  cursor = g.conn.execute("SELECT * FROM transa_transf WHERE created_time = %s", id)
  trx = cursor.fetchall()
  cursor = g.conn.execute("SELECT * FROM transa_transf WHERE created_time = %s", id)
  date = cursor.fetchone()
  return render_template('/trx.html', trx=trx, date=date)


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
