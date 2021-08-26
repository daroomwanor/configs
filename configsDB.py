import sqlite3
import json
from flask import render_template, request, jsonify, make_response
connection = sqlite3.connect("configs.db")

cursor = connection.cursor()

job_arg = json.dumps([])
d = '"'+job_arg+'"'
q="CREATE TABLE configsTable (\
Id INTEGER PRIMARY KEY,\
username varchar(200) DEFAULT NULL,\
cloudName varchar(200) DEFAULT NULL,\
status varchar(200) DEFAULT NULL,\
job_arguments blob,\
runTimeStamp timestamp NULL DEFAULT CURRENT_TIMESTAMP)"


job_q="CREATE TABLE jobsTable (\
Id INTEGER PRIMARY KEY,\
name varchar(200) DEFAULT NULL,\
jobType varchar(200) DEFAULT NULL,\
status varchar(200) DEFAULT NULL,\
job_arguments blob,\
runTimeStamp timestamp NULL DEFAULT CURRENT_TIMESTAMP)"

insertRoot='INSERT INTO configsTable (username, cloudname, status, job_arguments) VALUES\
("root", "service", "new",'+d+')'


from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<p>Welcome, Ariel Cloud User!</p>"

@app.route("/queryCloudVM/")
def queryCloudVM():
    cmd = request.args.get('q')
    print(cmd)
    commit = request.args.get('commit')
    cursor = connection.cursor()
    rows = cursor.execute(cmd).fetchall()
    connection.commit()
    resp = json.dumps(rows)
    return resp

@app.route("/bashCloudVM/", methods=['GET', 'POST'])
def bashCloudVM():
    cmd = request.args.get('cmd')
    stream = os.popen(cmd)
    output = stream.readlines()
    return output

if __name__ == '__main__':
    app.run()

