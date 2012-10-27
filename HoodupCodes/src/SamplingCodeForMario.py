import sys, csv, random, re
from collections import defaultdict as dd
from happyfuntokenizing import Tokenizer

class DataSampler():
  def __init__(self, dataFile):
    self.__data = []
    self.__commWiseIndices = {}
    self.__commWiseSampleIndices = {}
    self.__read(dataFile)
    self._tok = Tokenizer(preserve_case=False)
    
  def __read(self, dataFile):
    dataFile = open(dataFile)
    dataFile.readline()
    csvReader = csv.reader(dataFile, quotechar='"', escapechar="\\")
    index = 0
    tempDD = dd(list)
    for record in csvReader:
      record = filter(lambda x:x.strip(), record)
      try:
        self.__data.append(tuple(record))
        tempDD[record[3]].append(index)
        index+=1
      except:
        pass
        ##print record
        ##sys.exit()
    for key, value in tempDD.iteritems():
      if key.find("Talk")>=0:
        self.__commWiseIndices[key] = value
    sys.stderr.write("Read "+str(index)+" records\n")
        
  def _tokenize(self, text):
    text =  text.strip()
    text = re.sub('[\s\n]+',' ', text)
    return self._tok.tokenize(text)
  
  def communityWiseSample(self):
    numPosts = 1000
    for key in self.__commWiseIndices.iterkeys():
      self.__commWiseSampleIndices[key] = random.sample(self.__commWiseIndices[key], numPosts)
      
  def prepareOutput(self, outputFile):
    outputFile = open(outputFile,'w')
    csvWriter = csv.writer(outputFile)
    for key in self.__commWiseSampleIndices.iterkeys():
      for index in self.__commWiseSampleIndices[key]:
        #tokens = self._tokenize(self.__data[index][1])
        csvWriter.writerow(self.__data[index])
    outputFile.close()

if __name__ == '__main__':
  dataFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts/hoodup_2012_10_22.csv"
  outputFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts/sampledData.csv"
  DS = DataSampler(dataFile)
  DS.communityWiseSample()
  DS.prepareOutput(outputFile)