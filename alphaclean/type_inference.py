import numpy as np

cat_thresh=1000
num_thresh=0.25


def getDataTypes(data, attrs):
	"""
	Given data in a list of lists format this returns a list 
	of attribute types
	"""

	type_array = {}

	for a in attrs:

		if __is_num(data[a]):
			type_array[a] = 'num'
		elif __is_cat(data[a]):
			type_array[a] = 'cat'
		else:
			type_array[a] = 'string'

	return type_array


def __is_num(data):
	"""
	Internal method to determine whether data is numerical
	"""
	float_count = 0.0

	for datum in data:
		try:
			float(datum.strip())
			float_count = float_count + 1.0
		except:
			#print datum
			pass

	return (float_count/len(data) > num_thresh)



def __is_cat(data):
	"""
	Internal method to determine whether data is categorical
	defaults to number of distinct values is N/LogN
	"""
	
	counts = {}

	for datum in data:
		d = datum

		if d not in counts:
			counts[d] = 0

		counts[d] = counts[d] + 1

	totalc = len([k for k in counts if counts[k] > 1])+0.0
	total = len([k for k in counts])+0.0

	return (totalc < cat_thresh) and (totalc/total > 0.2)


