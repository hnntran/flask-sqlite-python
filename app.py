from inspect import stack
from operator import index
from flask import Flask, render_template
import sqlite3
import pandas as pd


app = Flask(__name__)


# Create 2 tagging tables:
con = sqlite3.connect("Cisco.db")
cur = con.cursor()
# tag table: id (Primary), tag
con.execute("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, tag TEXT NOT NULL)")
cur.execute("INSERT OR IGNORE INTO tags (id,tag) VALUES (1,'dev'),(2,'staging'),(3,'prod')")
# device_tag table: tag_id (= tags.id), device_id (= devices.id)
con.execute("CREATE TABLE IF NOT EXISTS device_tag (tag_id TEXT, device_id TEXT, UNIQUE(tag_id,device_id), FOREIGN KEY(tag_id) REFERENCES tags(id))")
cur.execute("INSERT OR IGNORE INTO device_tag (tag_id, device_id) SELECT t.id as tag_id,d.id as device_id FROM devices d, tags t WHERE d.tags like '%dev%' and t.tag = 'dev'")
cur.execute("INSERT OR IGNORE INTO device_tag (tag_id, device_id) SELECT t.id as tag_id,d.id as device_id FROM devices d, tags t WHERE d.tags like '%staging%' and t.tag = 'staging'")
cur.execute("INSERT OR IGNORE INTO device_tag (tag_id, device_id) SELECT t.id as tag_id,d.id as device_id FROM devices d, tags t WHERE d.tags like '%prod%' and t.tag = 'prod'")

con.commit()
con.close()


def get_db_connection():
    conn = sqlite3.connect('Cisco.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home page:
@app.route("/")
def home():
    conn = get_db_connection()
    query1 = 'SELECT * from devices'
    query2 = 'SELECT * from device_interfaces limit 10'
    devices = conn.execute(query1).fetchall()
    device_interfaces = conn.execute(query2).fetchall()
    conn.close()
    return render_template('index.html', data1=devices, data2=device_interfaces)

# Endpoint: /device/{colocation}
@app.route("/device/<colocation>")
def device_colocation(colocation):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    query = "SELECT * FROM devices WHERE colocation = '{n}'".format(n=colocation)
    colocation_list = cursor.execute('SELECT DISTINCT colocation FROM devices').fetchall()
    if colocation in colocation_list:
        conn.row_factory = sqlite3.Row
        devices = conn.execute(query).fetchall()
        conn.close()
        return render_template('device_colocation.html', data1=devices)
    else:
        conn.close()
        result = 'No such device'
    return result

# Endpoint: /interface/{type}/{status}
@app.route("/interface/<type>/<status>")
def interfaces(type,status):
    conn = get_db_connection()
    # use pandas Dataframe to store data
    interfaces = pd.read_sql('SELECT * FROM device_interfaces', conn)
    conn.close()
    # filter by type and status
    result = interfaces.loc[(interfaces['type'] == '{n}'.format(n=type)) & (interfaces['status'] == '{m}'.format(m=status))]
    count_row = result.shape[0]
    return render_template('interfaces.html', data1=[result.to_html()], 
        titles=[''], type=type, status=status, count_row=count_row)

# Endpoint: /device/{id}/tags
@app.route("/device/<id>/tags")
def device_tags(id):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    query = "SELECT tags FROM devices WHERE id = '{n}'".format(n=id)
    device_id_list = cursor.execute('SELECT id FROM devices').fetchall()
    if id in device_id_list:
        conn.row_factory = sqlite3.Row
        tags = conn.execute(query).fetchall()
        conn.close()
        return render_template('device_tags.html', data1=tags, id=id)
    else:
        conn.close()
        result = 'No such device'
    return result

# Endpoint: /tags/{tag_id}/device
@app.route("/tags/<tag_id>/device")
def tags(tag_id):
    conn = get_db_connection()
    query = "SELECT d.* FROM devices d JOIN device_tag t ON t.device_id = d.id WHERE t.tag_id = {n}".format(n=tag_id)
    devices = conn.execute(query).fetchall()
    conn.close()
    return render_template('tags.html', data1=devices)


if __name__ == "__main__":
    app.run()
