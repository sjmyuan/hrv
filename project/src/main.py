import rpeakdetect
import hrv
from bottle import run,post,request
import sqlite3
import db
import os

#initialize database
dbi=db.DBI('data/hrv.db')
dbi.initialize()

def recordingData(data):
    time=data['time']
    user=data['user']
    timeInterval=data['time_interval']
    sampleRate=data['sample_rate']
    label=data['label']
    originData=data['origin_data']
    print data
    print originData
    sql="insert into origindata values(?,?,?,?,?,?)"
    dbi.execute(sql,
            [time,user,
                str(timeInterval),
                str(sampleRate),
                label,
                str(originData)])

def calcFeatures(data):
    print 'haha'

def recordingFeatures(data):
    print 'haha'

@post('/data')
def serve_data():
    data=request.json  
    recordingData(data)

    originData=data['origin_data']
    features=calcFeatures(originData)
    recordingFeatures(features)
    return '{"emotion_changed":True}'

run(host='localhost', port=8080, debug=True)
