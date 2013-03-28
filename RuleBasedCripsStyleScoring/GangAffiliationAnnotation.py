import os

if __name__ == '__main__':
  gangsFolder = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/BasicData/Affiliations/gangs"
  affilsFile = "/usr0/home/pgadde/Work/Ethnic/Hoodup/Data/Nov2012/BasicData/Affiliations/userGangs.tsv"
  gangDict = {}
  for file in os.listdir(gangsFolder):
    users = set([l.strip().split('\t')[0] for l in open(gangsFolder+'/'+file)])
    for user in users:
      if user not in gangDict.keys():
        gangDict[user] = file
      else:
        print user, file, gangDict[user]
  affilsFile = open(affilsFile,'w')
  for user in gangDict.iterkeys():
    affilsFile.write(user+'\t'+gangDict[user]+'\n')
  affilsFile.close()