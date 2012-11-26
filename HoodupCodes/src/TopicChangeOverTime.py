import sys, csv, codecs
csv.field_size_limit(1000000000)
from DataHandler import DataHandler
from collections import defaultdict as dd

class TopicChange:
  def __init__(self, dataFile, userJoins, activeForums):
    sys.stderr.write("Started\n")
    self.dataHandler = DataHandler(dataFile, userJoins)
    self.dataHandler.loadActiveForums(activeForums)
    sys.stderr.write("Data loaded\n")
    self.post2Month = self.dataHandler.getPost2Month()
    self.doc2Post = self.dataHandler.getDoc2Post()
    self.post2User = self.dataHandler.getPost2User()
    sys.stderr.write("Got the dicts\n")
  
  def loadInferredTopics(self, topicsOutput):
    userMonth = dd(lambda:dd(int))
    numUsers = set()
    csvReader = csv.reader(open(topicsOutput))
    for doc in csvReader:
      #if len(doc)<21:
      #  continue
      #print 'phani'
      docId = doc[0]
      #topic5Num = doc[5]
      #topic19Num = doc[19]
      userId = self.post2User[self.doc2Post[docId]]
      #month = self.post2Month[self.doc2Post[docId]]
      #userMonth[userId][month] += topic5Num
      numUsers.add(userId)
    #for user in userMonth.iterkeys():
    #  for month in userMonth[user].iterkeys():
    #    print user, month, userMonth[user][month]
    print len(numUsers)

def prepareUserMonthInfo(topicsInput):
    userMonthDocInfo = dd(lambda:dd(list))
    userMonthMetaInfo = dd(lambda:dd(list))
    f = codecs.open(topicsInput,encoding='utf-8')
    reader = csv.reader(f)
    for line in reader:
      userMonthDocInfo[line[1]][line[2]].append(line[0])
      userMonthMetaInfo[line[1]][line[2]] = [line[3],line[-1]]
    return userMonthDocInfo, userMonthMetaInfo
  
def prepareUserMonthInfoWithForum(topicsInput):
    userMonthDocInfo = dd(lambda:dd(lambda:dd(list)))
    userMonthMetaInfo = dd(lambda:dd(lambda:dd(list)))
    f = codecs.open(topicsInput,encoding='utf-8')
    reader = csv.reader(f)
    for line in reader:
      userMonthDocInfo[line[1]][line[2]][line[-1]].append(line[0])
      userMonthMetaInfo[line[1]][line[2]][line[-1]] = [line[3],line[-2]]
    return userMonthDocInfo, userMonthMetaInfo
  
def prepareDocTopicInfo(topicsOutput):
    docTopicInfo = dd(list)
    f = codecs.open(topicsOutput,encoding='utf-8')
    reader = csv.reader(f)
    for line in reader:
      docTopicInfo[line[0]] = line[1:]
    return docTopicInfo

def getRequiredTopicScores(topicScores):
  #if len(topicScores)<20:
  #  print topicScores
  return [round(float(topicScores[4]),2),round(float(topicScores[14]),2)]

def printTopicsOverTime(topicsInput, topicsOutput):
    userMonthDocInfo, userMonthMetaInfo = prepareUserMonthInfo(topicsInput)
    docTopicInfo = prepareDocTopicInfo(topicsOutput)
    for user in userMonthMetaInfo.iterkeys():
      if len(userMonthMetaInfo[user])<3:
        continue
      for month in userMonthMetaInfo[user].iterkeys():
        if int(month)>100:
          continue
        forum = userMonthMetaInfo[user][month][0]
        numPosts = userMonthMetaInfo[user][month][1]
        doc = userMonthDocInfo[user][month][0]
        stuffToPrint = [user, month, forum, numPosts]
        stuffToPrint.extend(getRequiredTopicScores(docTopicInfo[doc]))
        if len(userMonthDocInfo[user][month]) > 0:
          print '\t'.join(map(lambda x:str(x), stuffToPrint))

def printTopicsOverTimeWithForum(topicsInput, topicsOutput, outFile):
    outFile = open(outFile,'w')
    userMonthDocInfo, userMonthMetaInfo = prepareUserMonthInfoWithForum(topicsInput)
    docTopicInfo = prepareDocTopicInfo(topicsOutput)
    for user in userMonthMetaInfo.iterkeys():
      if len(userMonthMetaInfo[user])<3:
        continue
      for month in userMonthMetaInfo[user].iterkeys():
        if int(month)>100:
          continue
        for postForum in userMonthMetaInfo[user][month].iterkeys():
          forum = userMonthMetaInfo[user][month][postForum][0]
          numPosts = userMonthMetaInfo[user][month][postForum][1]
          doc = userMonthDocInfo[user][month][postForum][0]
          stuffToPrint = [user, month, forum, numPosts, postForum]
          #stuffToPrint = [user, month, forum, numPosts]
          stuffToPrint.extend(getRequiredTopicScores(docTopicInfo[doc]))
          if len(userMonthDocInfo[user][month]) > 0:
            outFile.write('\t'.join(map(lambda x:str(x), stuffToPrint))+'\n')
            print '\t'.join(map(lambda x:str(x), stuffToPrint))
    outFile.close()

if __name__ == '__main__':
  baseDir = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/TopicChange/TopicModelling/"
  #dataFile = baseDir + "LDAsampledData.csv"
  #userJoins = baseDir + "userJoins"
  #activeForums = baseDir + "activeForums.csv"
  #TC = TopicChange(dataFile, userJoins, activeForums)
  topicsOutput = baseDir+"lda-b76b9ca4-20-6044337b/tmtInputATUserMonthDocsWithForum-document-topic-distributuions.csv"
  topicsInput = baseDir+"tmtInputATUserMonthDocsWithForum.csv"
  outFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/DataExploration/SampledPosts2/TopicChange/topicChangeWithPostForums.tsv"
  printTopicsOverTimeWithForum(topicsInput, topicsOutput, outFile)