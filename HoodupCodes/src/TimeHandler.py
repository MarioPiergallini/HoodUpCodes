class TimeHandler:
  def __init__(self):
    self.__months = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}
  
  def diffMonths(self, time1, time2):
    #print time1, time2
    try:
      year1 = int(time1.split(',')[1].strip())
      year2 = int(time2.split(',')[1].strip())
      diff = 0
      if year1 > year2:
        temp = time1
        time1 = time2
        time2 = temp
        diff = (year1 - year2 - 1) * 12
      elif year1 < year2:
        diff = (year2 - year1 - 1) * 12
      month1 = time1.split(' ')[0]
      month2 = time2.split(' ')[0]
      diff += 12 - self.__months[month1] + self.__months[month2]
      #if diff < 0:
      #  print year1, year2, time1, time2
      return diff
    except IndexError:
      print time1, time2
      return -1
  
  def diffWeeks(self, time1, time2):
    ## Didn't implement yet
    year1 = int(time1.split(',')[1].strip())
    year2 = int(time2.split(',')[1].strip())
    diff = 0
    if year1 > year2:
      temp = time1
      time1 = time2
      time2 = temp
      diff = (year1 - year2 - 1) * 12
    elif year1 < year2:
      diff = (year2 - year1 - 1) * 12
    month1 = time1.split(' ')[0]
    month2 = time2.split(' ')[0]
    diff += 12 - self.__months[month1] + self.__months[month2]
    #if diff < 0:
    #  print year1, year2, time1, time2
    return diff