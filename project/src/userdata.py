import rpeakdetect
from hrv.classical import time_domain, frequency_domain
import pickle
import numpy
import sklearn.preprocessing as sk
from sklearn.ensemble import IsolationForest
from scipy import interpolate

class HRV:
    def __init__(self,originData,dbi):
        '''
        all time unit is millisecond 
        '''
        self.time=originData['time']
        self.user=originData['user']
        self.timeInterval=originData['time_interval']
        self.sampleRate=float(originData['sample_rate'])
        self.label=originData['label']
        self.originData=originData['origin_data']
        self.originTime=originData.get('origin_time',None)
        self.samples=self.originData
        self.features={}
        self.dbi=dbi
        self.status='normal'
        self.featureIndex=['hf', 'hfnu', 'lf', 'lf_hf', 'lfnu', 'mhr', 'mrri', 'nn50', 'pnn50', 'rmssd', 'sdnn', 'total_power', 'vlf']

    def resample(self):
        if self.originTime is not None:
            self.time=self.originTime[0]
            self.timeInterval=self.originTime[-1]-self.originTime[0]
            self.sampleRate=200
            xcord=numpy.linspace(self.originTime[0], self.originTime[-1], int(self.timeInterval*self.sampleRate/1000.0))
            # self.samples=numpy.interp(xcord,self.originTime,self.originData)
            func=interpolate.interp1d(self.originTime,self.originData,kind='cubic')
            self.samples=func(xcord)

    def recording(self):
        sql="insert into originData values(?,?,?,?,?,?)"
        self.dbi.execute(sql,
                [
                    self.time,
                    self.user,
                    self.timeInterval,
                    self.sampleRate,
                    self.label,
                    pickle.dumps(self.originData)
                ])

        sql="insert into featureData values(?,?,?,?)"
        self.dbi.execute(sql,[
            self.time,
            self.user,
            self.status,
            pickle.dumps(self.features)
            ])

    def getLatestFeatures(self,user):
        sql="select features from featureData where user='%s' and status='normal' order by time desc limit 1000" % user
        data=map(lambda x:pickle.loads(x[0]),self.dbi.query(sql)) 
        return data if len(data)>0 else None

    def setStatusByStd(self,featureNames):
        oldFeatures=self.getLatestFeatures(self.user)
        if oldFeatures is not None and len(oldFeatures)>5:
            featuresMatrix=map(lambda x: [x[name] for name in featureNames],oldFeatures)
            featuresMatrix+=[[self.features[name] for name in featureNames]]

            featuresMatrix=sk.normalize(featuresMatrix,axis=0)
            oldStd=numpy.round(numpy.std(featuresMatrix[:-1],axis=0),5)
            newStd=numpy.round(numpy.std(featuresMatrix,axis=0),5)
            nonZeroIndex=numpy.nonzero(oldStd)
            if nonZeroIndex[0].size>0:
                if numpy.max(abs(newStd[nonZeroIndex]-oldStd[nonZeroIndex])/oldStd[nonZeroIndex]) > 0.3:
                    self.status='unnormal'


    def setStatusByProbability(self,featureNames):
        oldFeatures=self.getLatestFeatures(self.user)
        if oldFeatures is not None and len(oldFeatures)>5:
            featuresMatrix=map(lambda x: [x[name] for name in featureNames],oldFeatures)
            featuresMatrix+=[[self.features[name] for name in featureNames]]

            featuresMatrix=sk.normalize(featuresMatrix,axis=0)
            newFeature=featuresMatrix[-1]
            std=numpy.round(numpy.std(featuresMatrix[:-1],axis=0),5)
            mean=numpy.round(numpy.mean(featuresMatrix[:-1],axis=0),5)
            probability=reduce(lambda x,y:x*y,numpy.exp(-1.0*(newFeature-mean)**2/(2*std**2))/(numpy.sqrt(2*numpy.pi*std)))
            if probability < 0.5:
                self.status='unnormal'
            
    def setStatusByIsolationForest(self,featureNames):
        oldFeatures=self.getLatestFeatures(self.user)
        if oldFeatures is not None and len(oldFeatures)>5:
            featuresMatrix=map(lambda x: [x[name] for name in featureNames],oldFeatures)
            newFeature=[[self.features[name] for name in featureNames]]
            clf=IsolationForest(max_samples=100, random_state=numpy.random.RandomState(42))
            clf.fit(featuresMatrix)
            result=clf.predict(newFeature)

            if result[0] < 0:
                self.status='unnormal'

    def emotionRecognizing(self):
        self.resample()

        #get NN interval array
        peakIndex=numpy.asarray( rpeakdetect.detect_beats(self.samples,self.sampleRate) )
        peakIndexHigh=peakIndex[1:] 
        peakIndexLow=peakIndex[:-1]
        nnInterval=(peakIndexHigh-peakIndexLow)*1000.0/self.sampleRate

        #calculate hrv features
        timeDomainFeatures=time_domain(nnInterval)
        frequencyDomainFeatures=frequency_domain(nnInterval,interp_freq=6.0,
                                                    method='welch', segment_size=10,
                                                    overlap_size=5,
                                                    window_function='hanning')
        self.features.update(timeDomainFeatures)
        self.features.update(frequencyDomainFeatures)

        #calculate feature difference
        # self.setStatusByStd(self.featureIndex)
        # self.setStatusByProbability(self.featureIndex)
        self.setStatusByIsolationForest(self.features) 

        self.recording()
        print self.features
        return {'emotion_changed': self.status == 'unnormal','heart_rate': self.features['mhr']}

