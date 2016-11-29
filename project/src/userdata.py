import rpeakdetect
from hrv.classical import time_domain, frequency_domain
import pickle
import numpy

class HRV:
    def __init__(self,originData):
        self.time=originData['time']
        self.user=originData['user']
        self.timeInterval=originData['time_interval']
        self.sampleRate=float(originData['sample_rate'])
        self.label=originData['label']
        self.originData=originData['origin_data']
        self.features={}

    def recording(self,dbi):
        sql="insert into originData values(?,?,?,?,?,?)"
        dbi.execute(sql,
                [
                    self.time,
                    self.user,
                    self.timeInterval,
                    self.sampleRate,
                    self.label,
                    pickle.dumps(self.originData)
                ])

        sql="insert into featureData values(?,?,?)"
        dbi.execute(sql,[
            self.time,
            self.user,
            pickle.dumps(self.features)
            ])

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
        return '{"emotion_changed":True,"heart_rate":%d}' % (self.features['mhr'])

