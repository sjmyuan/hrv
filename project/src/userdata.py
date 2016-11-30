import rpeakdetect
from hrv.classical import time_domain, frequency_domain
import pickle
import numpy
import sklearn.preprocessing as sk

class HRV:
    def __init__(self,originData,dbi):
        self.time=originData['time']
        self.user=originData['user']
        self.timeInterval=originData['time_interval']
        self.sampleRate=float(originData['sample_rate'])
        self.label=originData['label']
        self.originData=originData['origin_data']
        self.features={}
        self.dbi=dbi
        self.status='normal'
        self.featureIndex=['hf', 'hfnu', 'lf', 'lf_hf', 'lfnu', 'mhr', 'mrri', 'nn50', 'pnn50', 'rmssd', 'sdnn', 'total_power', 'vlf']

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
        sql="select features from featureData where user='%s' and status='normal' order by time desc limit 10" % user
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
            

    def emotionRecognizing(self):
        #get NN interval array
        peakIndex=numpy.asarray( rpeakdetect.detect_beats(self.originData,self.sampleRate) )
        peakIndexHigh=peakIndex[1:] 
        peakIndexLow=peakIndex[:-1]
        nnInterval=(peakIndexHigh-peakIndexLow)/self.sampleRate*1000

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
        self.setStatusByProbability(self.featureIndex)

        self.recording()
        return '{"emotion_changed":%s,"heart_rate":%d}' % (self.status=='normal',self.features['mhr'])

