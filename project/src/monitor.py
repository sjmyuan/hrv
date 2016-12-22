import sqlite3
import pickle
import db
import os
from json import dumps
import matplotlib.pyplot as plt
import argparse
import numpy
from sklearn.ensemble import IsolationForest

#initialize database
dbFile=os.getenv('DB_FILE', 'hrv.db')
dbi=db.DBI(dbFile)
features=['hf', 'hfnu', 'lf', 'lf_hf', 'lfnu', 'mhr', 'mrri', 'nn50', 'pnn50', 'rmssd', 'sdnn', 'total_power', 'vlf']
def create_parser():
    parser = argparse.ArgumentParser(description='view feature data')    
    parser.add_argument('user', action="store",type=str)
    parser.add_argument('len', action="store",type=int)
    parser.add_argument('type', action="store",type=str)
    return parser

def show_feature(user,dataLen):
    sql="select features from featureData where user='%s' order by time asc limit %d" % (user,dataLen)
    data=map(lambda x:pickle.loads(x[0]),dbi.query(sql)) 
    figureNum=1
    fig=plt.figure(1)
    for name in features:
        featureData=map(lambda x: x[name],data)
        fig.add_subplot(7,2,figureNum)
        plt.title(name)
        plt.plot(featureData)
        figureNum+=1
    plt.show()

def show_raw(user,dataLen):
    sql="select data from originData where user='%s' order by time asc limit %d" % (user,dataLen)
    data=dbi.query(sql)
    data=numpy.array(pickle.loads(data[-1][0]))
    
    plt.figure(1)
    plt.plot(data.flatten())
    plt.show()

def validate(user,dataLen):
    sql="select data from originData where user='%s' order by time asc limit %d" % (user,dataLen)
    data=dbi.query(sql)
    data=pickle.loads(data[-1][0])
    clf=IsolationForest(max_samples=100, random_state=numpy.random.RandomState(42))
    clf.fit(featuresMatrix)
    result=clf.predict(newFeature)

    if result[0] < 0:
        self.status='unnormal'

if __name__ == "__main__":
    parser=create_parser()
    paras=parser.parse_args()
    user=paras.user
    dataLen=paras.len
    showType=paras.type

    if showType == 'feature':
        show_feature(user,dataLen)

    if showType == 'raw':
        show_raw(user,dataLen)

