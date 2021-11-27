import re
import pprint
# app.py
from flask import Flask, request, render_template, jsonify, json, jsonify, redirect, url_for, session, Blueprint, \
    current_app
from flaskext.mysql import MySQL  # pip install flask-mysql

from dbMysql import query_data, insert_or_update_data
import pymysql

app = Flask(__name__)
app.secret_key = "mulancompany"
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'bobpwd'
app.config['MYSQL_DATABASE_DB'] = 'mulan'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
# @app.route('/pythonlogin/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    print('here is login func request.method=' + request.method)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        sql = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        datas = query_data(sql)
        if len(datas) > 0:
            account = datas[0]
            print(account['idaccount'])
            # Fetch one record and return result
            # account = cursor.fetchone()
            # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['idaccount']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                print('Incorrect username/password!')
                msg = 'Incorrect username/password!'

        else:
            print("没有找到记录")
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg=msg)


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout')
# @app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
# @app.route('/register', methods=['GET', 'POST'])
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        password1 = request.form['password1']
        print(password, password1)
        if password1 == password:
            print("进来了")
            email = request.form['email']
            # Check if account exists using MySQL
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            sql = f"SELECT * FROM user WHERE username ='{username}'"
            print(sql)
            datas = query_data(sql)
            if datas:
                account = datas[0]
            else:
                account = datas
            # account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                # cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
                # mysql.connection.commit()
                # sql = 'INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,)
                sql = f"INSERT INTO user VALUES (NULL, '{username}', '{password}', '{email}')"
                print(sql)
                insert_or_update_data(sql)
                msg = 'You have successfully registered!'
        else:
            msg = 'Password was diffrent!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
# @app.route('/home', methods=['GET', 'POST'])
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        # sql = "select * from loads"

        sql = "SELECT load_num,driver_name,truck_name,DATE_FORMAT(pickup, '%m-%d-%Y') as pick,DATE_FORMAT(delivery, '%m-%d-%Y') as diliver,trip,DH_O,rate,rate/(trip+DH_O) as price,origin_address,origin_state,destination_address,destination_state,customer FROM mulan.loads;"
        print(sql)
        datas = query_data(sql)
        return render_template("loadlisting.html", datas=datas, username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/dispatch - this will be the dispatch page, only accessible for loggedin users
@app.route('/dispatch', methods=['GET', 'POST'])
# @app.route('/pythonlogin/dispatch')
def dispatch():
    print("request==" + request.method)
    if request.method == 'POST':
        # Create variables for easy access
        load_num = request.form['load_num']
        po_num = request.form['po_num']
        load_status = request.form['load_status']
        driver_name = request.form['driver_name']
        truck_name = request.form['truck_name']
        pickup = request.form['pickup']
        delivery = request.form['delivery']
        avail = request.form['avail']
        origin_address = request.form['origin_address']
        origin_state = request.form.get('origin_state')
        destination_address = request.form['destination_address']
        destination_state = request.form.get('destination_state')
        customer = request.form['customer']
        trip = request.form['trip']
        DH_O = request.form['DH_O']
        rate = request.form['rate']
        weight = request.form['weight']
        length = request.form['length']
        contact_person = request.form['contact_person']
        contact_tel = request.form['contact_tel']
        contact_fax = request.form['contact_fax']
        contact_email = request.form['contact_email']
        p1_address = request.form['p1_address']
        p2_address = request.form['p2_address']
        p3_address = request.form['p3_address']
        note = request.form['note']
        sql = "INSERT INTO loads ("
        sql = sql if load_num == "" else sql + "load_num,"
        sql = sql if po_num == "" else sql + "po_num,"
        sql = sql if load_status == "" else sql + "load_status,"
        sql = sql if driver_name == "" else sql + "driver_name,"
        sql = sql if truck_name == "" else sql + "truck_name,"
        sql = sql if pickup == "" else sql + "pickup,"
        sql = sql if delivery == "" else sql + "delivery,"
        sql = sql if avail == "" else sql + "avail,"
        sql = sql if origin_address == "" else sql + "origin_address,"
        sql = sql if origin_state == "" else sql + "origin_state,"
        sql = sql if destination_address == "" else sql + "destination_address,"
        sql = sql if destination_state == "" else sql + "destination_state,"
        sql = sql if customer == "" else sql + "customer,"
        sql = sql if trip == "" else sql + "trip,"
        sql = sql if DH_O == "" else sql + "DH_O,"
        sql = sql if rate == "" else sql + "rate,"
        sql = sql if contact_person == "" else sql + "contact_person,"
        sql = sql if contact_tel == "" else sql + "contact_tel,"
        sql = sql if contact_email == "" else sql + "contact_email,"
        sql = sql if contact_fax == "" else sql + "contact_fax,"
        sql = sql if length == "" else sql + "length,"
        sql = sql if weight == "" else sql + "weight,"
        sql = sql if p1_address == "" else sql + "p1_address,"
        sql = sql if p2_address == "" else sql + "p2_address,"
        sql = sql if p3_address == "" else sql + "p3_address,"
        sql = sql if note == "" else sql + "note"
        if (sql[len(sql) - 1]) == ",":
            sql = sql[0:len(sql) - 1]
        sql = sql + ") VALUES("
        sql = sql if load_num == "" else sql + f"'{load_num}',"
        sql = sql if po_num == "" else sql + f"'{po_num}',"
        sql = sql if load_status == "" else sql + f"'{load_status}',"
        sql = sql if driver_name == "" else sql + f"'{driver_name}',"
        sql = sql if truck_name == "" else sql + f"'{truck_name}',"
        sql = sql if pickup == "" else sql + f"'{pickup}',"
        sql = sql if delivery == "" else sql + f"'{delivery}',"
        sql = sql if avail == "" else sql + f"'{avail}',"
        sql = sql if origin_address == "" else sql + f"'{origin_address}',"
        sql = sql if origin_state == "" else sql + f"'{origin_state}',"
        sql = sql if destination_address == "" else sql + f"'{destination_address}',"
        sql = sql if destination_state == "" else sql + f"'{destination_state}',"
        sql = sql if customer == "" else sql + f"'{customer}',"
        sql = sql if trip == "" else sql + f"'{trip}',"
        sql = sql if DH_O == "" else sql + f"'{DH_O}',"
        sql = sql if rate == "" else sql + f"'{rate}',"
        sql = sql if contact_person == "" else sql + f"'{contact_person}',"
        sql = sql if contact_tel == "" else sql + f"'{contact_tel}',"
        sql = sql if contact_email == "" else sql + f"'{contact_email}',"
        sql = sql if contact_fax == "" else sql + f"'{contact_fax}',"
        sql = sql if length == "" else sql + f"'{length}',"
        sql = sql if weight == "" else sql + f"'{weight}',"
        sql = sql if p1_address == "" else sql + f"'{p1_address}',"
        sql = sql if p2_address == "" else sql + f"'{p2_address}',"
        sql = sql if p3_address == "" else sql + f"'{p3_address}',"
        sql = sql if note == "" else sql + f"'{note}'"
        if (sql[len(sql) - 1]) == ",":
            sql = sql[0:len(sql) - 1]
        sql = sql + ")"

        # sql="INSERT INTO loads (load_num,po_num,load_status,driver_name,truck_name,pickup,delivery,avail,origin_address,origin_state,destination_address,destination_state,customer,trip,DH_O,rate,contact_person,contact_tel,contact_email,contact_fax,length,weight,p1_address,p2_address,p3_address,note) VALUES "+\
        #    f"('{load_num}', '{po_num}', '{load_status}', '{driver_name}', '{truck_name}', '{pickup}', '{delivery}', '{avail}', '{origin_address}', '{origin_state}', '{destination_address}', '{destination_state}', '{customer}', '{trip}', '{DH_O}', '{rate}', '{contact_person}', '{contact_tel}', '{contact_email}', '{contact_fax}', '{length}', '{weight}', '{p1_address}', '{p2_address}', '{p3_address}', '{note}')"
        print(sql)
        insert_or_update_data(sql)
        # print(load_num,po_num,load_status,driver_name,truck_name,pickup,delivery,avail,origin_address,origin_state,destination_address,destination_state)
        # print(customer,trip,DH_O,rate,weight,length,contact_person,contact_tel,contact_fax,contact_email,p1_address,p2_address,p3_address,note)

    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the dispatch page
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        # account = cursor.fetchone()
        sql = f"SELECT * FROM user WHERE idaccount = {session['id']}"
        datas = query_data(sql)
        account = datas[0]

        sql = "SELECT * FROM employee where role='Driver' and active=1"
        dir_names = query_data(sql)

        sql = "SELECT assets_name FROM assets where assets_type='Truck tractor' order by assets_name"
        truck_names = query_data(sql)

        sql = "SELECT * FROM load_status"
        load_status = query_data(sql)

        sql = "SELECT * FROM us_state"
        us_states = query_data(sql)

        # Show the dispatch page with account info
        return render_template('dispatch.html', dir_names=dir_names, truck_names=truck_names, load_status=load_status,
                               us_states=us_states, account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route("/ajaxfile", methods=["POST", "GET"])
def ajaxfile():
    print("ajaxfile function request.method=" + request.method)
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            # 以下这两个参数是为order使用的，一个是升降序，一个是当前选择的列
            order = request.form["order[0][dir]"]
            order_column = request.form["order[0][column]"]
            order_by = request.form[f"columns[{int(order_column)}][data]"]

            print(f"order={order}")
            print(f"order_column={order_column}")
            print(f"order_by={order_by}")

            print(f"draw={draw}")
            print(f"row={row}")
            print(f"rowperpage={rowperpage}")
            print(f"searchValue={searchValue}")
            idis = request.values
            print(idis)
            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from loads")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            print(f"likeString={likeString}")
            cursor.execute(
                "SELECT count(*) as allcount from loads WHERE driver_name LIKE %s OR truck_name LIKE %s OR origin_address LIKE %s",
                (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
            print(f"totalRecordwithFilter={totalRecordwithFilter}")

            ## Fetch records
            if searchValue == '':
                strSql = "SELECT * FROM loads ORDER BY delivery desc limit %s, %s;"
                print(f'strSql={strSql}')
                cursor.execute(strSql, (row, rowperpage))
                employeelist = cursor.fetchall()
            else:
                strSql = "SELECT * FROM loads WHERE driver_name LIKE %s OR truck_name LIKE %s OR origin_address LIKE %s limit %s, %s;"
                print(f'strSql={strSql}')
                cursor.execute(
                    strSql,
                    (likeString, likeString, likeString, row, rowperpage))
                employeelist = cursor.fetchall()

            data = []
            for row in employeelist:
                dho = row['DH_O']
                rate = f"${row['rate']}"
                unit_price = float(row['rate']) /(float(row['DH_O']) + float(row['trip']))
                print(f"unit_price={unit_price}")
                if row['pickup']:
                    pickup1 = (row['pickup'].strftime("%m-%d-%y %H:%M"))
                else:
                    pickup1 = ""
                if row['delivery']:
                    delivery = row['delivery'].strftime("%m-%d-%y %H:%M")
                else:
                    delivery = ""

                if row['avail']:
                    avail = (row['avail'].strftime("%m-%d-%y %H:%M"))
                else:
                    avail = ""

                data.append({
                    'idloads': row['idloads'],
                    'load_num': row['load_num'],
                    'po_num': row['po_num'],
                    'load_status': row['load_status'],
                    'driver_name': row['driver_name'],
                    'truck_name': row['truck_name'],
                    'origin_address': row['origin_address'],
                    'origin_state': row['origin_state'],
                    'destination_address': row['destination_address'],
                    'destination_state': row['destination_state'],
                    'pickup': pickup1,
                    'delivery': delivery,
                    'avail': avail,
                    'trip': row['trip'],
                    'DH_O': dho,
                    'rate': rate,
                    'unit_price': round(unit_price,2),
                    'contact_person': row['contact_person'],
                    'contact_tel': row['contact_tel'],
                    'contact_email': row['contact_email'],
                    'contact_fax': row['contact_fax'],
                    'length': row['length'],
                    'weight': row['weight'],
                    'p1_address': row['p1_address'],
                    'p2_address': row['p2_address'],
                    'p3_address': row['p3_address'],
                    'note': row['note'],

                })
            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/pythonlogin/account')
def account():
    return render_template('accounting.html')

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=False)
