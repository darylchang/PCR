# -*- coding: utf-8 -*-
import itertools, sys
import csv

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

REAGENT_MAP = {0: 'PRIMER', 1: 'TAQ', 2: 'DNTP', 3: 'BUFFER', 4: 'BIVALENT_CATION', 5: 'MONOVALENT_CATION'}
REVERSE_REAGENT_MAP = {'PRIMER': 0, 'TAQ': 1, 'DNTP': 2, 'BUFFER': 3, 'BIVALENT_CATION': 4, 'MONOVALENT_CATION': 5}

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
	def __init__(self, reagent, id, manufacturer, state=None):
		self.id = id
		self.manufacturer = manufacturer
		self.reagent = reagent
		self.state = state
	
	def is_same_aliquot(self, other):
		return self.reagent == other.reagent and self.id == other.id and self.manufacturer == other.manufacturer
		
class PCRDatabase:
	def __init__(self):
		self.pcrs = list()
		
	def __init__(self, filename):
		self.pcrs = list()
		f = open(filename, 'r')
		n_pcrs = int(f.readline())
		# Throw away hard return
		f.readline()
		for i in range(n_pcrs):
			pos_control_result = f.readline() == 'True'
			neg_control_result = f.readline() == 'True'
			aliquots = list()
			line = f.readline()
			while len(line.strip()) != 0:
				aliquot = self.parse_reagent_line(line.split())
				aliquots.append(aliquot)
				line = f.readline()
			pcr = PCR(pos_control_result, neg_control_result, aliquots)
			self.add_pcr(pcr)
		# TODO: parse some probabilities.
		
	def parse_reagent_line(self, words):
		reagent = REVERSE_REAGENT_MAP[words[0]]
		id = words[1]
		manufacturer = words[2]
		return Aliquot(reagent, id, manufacturer)
	
	def add_pcr(self, pcr):
		self.pcrs.append(pcr)
	
	def get_all_aliquots(self):
		aliquots = [pcr.aliquots for pcr in self.pcrs]
		return set([i for i in itertools.chain.from_iterable(aliquots)])
		
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
	
