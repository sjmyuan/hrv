from bottle import run,post,request,response
import sqlite3
import db
import os
import userdata
from json import loads,dumps

#initialize database
dbFile=os.getenv('DB_FILE', 'hrv.db')
dbi=db.DBI(dbFile)

@post('/data')
def serve_data():
    data=request.json 
    # data=data if data is not None else loads('{%s}' % request.body.read())
    hrv=userdata.HRV(data,dbi)
    result=hrv.emotionRecognizing()
    print result
    response.content_type = 'application/json'
    return dumps(result)

run(host='0.0.0.0', port=8080, debug=True)
