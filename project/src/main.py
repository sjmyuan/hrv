from bottle import run,post,request
import sqlite3
import db
import os
import userdata

#initialize database
dbFile=os.getenv('DB_FILE', 'hrv.db')
dbi=db.DBI(dbFile)

@post('/data')
def serve_data():
    data=request.json  
    hrv=userdata.HRV(data)
    result=hrv.emotionRecognizing()
    hrv.recording(dbi)
    return result

run(host='localhost', port=8080, debug=True)
