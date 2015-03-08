# -*- coding: utf-8 -*-
import sys

"""
This is really fragile. 
TODO: Figure out a way to better integrate with the ontology.
""" 
PRIMER = 0
TAQ = 1
DNTP = 2
BUFFER = 3
BIVALENT_CATION = 4
MONOVALENT_CATION = 5

class PCR:
	def __init__(self, pos_control_result, negative_control_result, aliquots):
		if pos_control_result == False and negative_control_result == True:
			raise Exception('Illegal PCR.')
		self.pos_control_result = pos_control_result
		self.negative_control_result = negative_control_result
		self.aliquots = list(aliquots)
	
	"""
	If a PCR has a defective reagent, it may also have contaminated reagents.
	In this case, however, the negative control would still come back negative,
	so had_contaminated_reagent would be false.
	"""
	def had_defective_reagent(self):
		return self.pos_control_result == False
		
	def had_contaminated_reagent(self):
		return self.negative_control_result == True

	def had_bad_reagent(self, error):
		if error == 'defective':
			return self.had_defective_reagent()
		elif error == 'contaminated':
			return self.had_contaminated_reagent()
	
	
class Aliquot:
	def __init__(self, reagent, id, manufacturer):
		self.id = id
		self.manufacturer = manufacturer
		self.reagent = reagent
	
	def is_same_aliquot(self, other):
		return self.reagent == other.reagent and self.id == other.id and self.manufacturer == other.manufacturer
		
class PCRDatabase:
	def __init__(self):
		self.pcrs = list()
		
	def add_pcr(self, pcr):
		self.pcrs.append(pcr)
		
	def pcrs_with_aliquot(self, aliquot):
		pcrs = list()
		for pcr in self.pcrs:
			for other in pcr.aliquots:
				if aliquot.is_same_aliquot(other):
					pcrs.append(pcr)
					# Break unnecessary, unless this aliquot is somehow duplicated 
					# in the pcr's aliquot list.
					break
		return pcrs	
	

    

