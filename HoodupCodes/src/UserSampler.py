import copy

class userSampling:
  def __init__(self, userWiseTimeSplitIndices):
    self.userWiseTimeSplitIndices = copy.deepcopy(userWiseTimeSplitIndices)

  def removeMorethan30(self):
    for user in self.userWiseTimeSplitIndices.iterkeys():
      months = self.userWiseTimeSplitIndices[user].keys()
      for month in months:
        try:
          if int(month) > 30:
            del self.userWiseTimeSplitIndices[user][month]
        except:
          del self.userWiseTimeSplitIndices[user][month]

  def removeNotAtleast5Posts(self):
    for user in self.userWiseTimeSplitIndices.iterkeys():
      months = self.userWiseTimeSplitIndices[user].keys()
      for month in months:
        if len(self.userWiseTimeSplitIndices[user][month])<5:
            del self.userWiseTimeSplitIndices[user][month]
    users = self.userWiseTimeSplitIndices.keys()
    for user in users:
      if not len(self.userWiseTimeSplitIndices[user]) > 0:
        del self.userWiseTimeSplitIndices[user]

  def removeNotAtLeast12(self):
    users = self.userWiseTimeSplitIndices.keys()
    for user in users:
      if not len(self.userWiseTimeSplitIndices[user]) > 11:
        del self.userWiseTimeSplitIndices[user]

  def removeNot10Initial(self):
    users = self.userWiseTimeSplitIndices.keys()
    for user in users:
      initialPostCount = 0
      for month in range(1,4):
        try:
          initialPostCount += len(self.userWiseTimeSplitIndices[user][month])
        except:
          pass
      if not initialPostCount > 9:
        del self.userWiseTimeSplitIndices[user]

  def removeNot10Matured(self):
    users = self.userWiseTimeSplitIndices.keys()
    for user in users:
      maturedPostCount = 0
      for month in range(25,31):
        try:
          maturedPostCount += len(self.userWiseTimeSplitIndices[user][month])
        except:
          pass
      if not maturedPostCount > 9:
        del self.userWiseTimeSplitIndices[user]