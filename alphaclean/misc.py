import re


def scan(d, attr, skip=set()):
   iindex = {}
   for i, st in enumerate(d[attr].values):

      for v in re.split('[^a-zA-Z]', str(st)):
         if v not in iindex:
            iindex[v] = []

         if i not in skip:
            iindex[v].append(i)

   return iindex


def generateTokenCodebook(d, attr, k=100):

   skiplist = set()

   return_set = set()

   while k > 0:
      iindex = scan(d, attr, skiplist)
      sortedList = sorted([(len(iindex[i]),i) for i in iindex], reverse=True)
      return_set.add(sortedList[0][1])
      skiplist = skiplist.union(set(iindex[sortedList[0][1]]))
      k = k - 1

   return return_set