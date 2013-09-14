def log(m):
	log.d = True
	print log.d, "Inside"
	if log.d: print m

class numArray(list):
	
	mode = "debug"
	def __getitem__(self, key):
		if isinstance(key, iter):
			print "Tuple" and (mode == "debug")
			return (list.__getitem__(self, key[0]))[key[1]]
		else:
			print "No Tuple" and (mode == "debug")
			return list.__getitem__(self, key[0])		


class loopBoard(object):
	
	order = 7
			
	def __init__(self, numArray):
		self.numArray = numArray
		
if __name__ == "__main__":
	
	
	log("Print")
	print type(log.d)
	print log.d
	log.d = False
	print log.d
	log("Don't Print")
	
		
