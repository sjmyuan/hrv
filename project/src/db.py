import sqlite3
import os.path

class DBI:
    def __init__(self,dbFile):
        self.dbFile=dbFile
        
    def execute(self,sql,args):
        conn = sqlite3.connect(self.dbFile)
        c=conn.cursor()
        c.execute(sql,args)
        conn.commit()
        conn.close()
        
    def initialize(self):
        if not os.path.isfile(self.dbFile):
            self.execute('create table originData(time TEXT,user TEXT,timeInterval INTEGER,sampleRate INT,label TEXT,data TEXT)',[])
            self.execute('create table featureData(time TEXT,user TEXT,features TEXT)',[])
