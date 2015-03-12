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

REAGENT_MAP = {0: 'PRIMER', 1: 'TAQ', 2: 'DNTP', 3: 'BUFFER', 4: 'BIVALENT', 5: 'MONOVALENT'}
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
	def __init__(self, filename=None):
		self.pcrs = list()
		# Error probabilities is a dictionary of (error, reagent, manufacturer) => prob.
		# Users supply any probabilities they can estimate.  The default probability is 0.1.
		self.error_probs = dict()
		if filename:
			f = open(filename, 'r')
			n_pcrs = int(f.readline())
			# Throw away hard return
			f.readline()
			all_aliquots = list()
			for i in range(n_pcrs):
				pos_control_result = f.readline().strip() == 'True'
				neg_control_result = f.readline().strip() == 'True'
				aliquots = list()
				line = f.readline()
				while len(line.strip()) != 0:
					aliquot = self.parse_reagent_line(line.split(), all_aliquots)
					aliquots.append(aliquot)
					line = f.readline()
				pcr = PCR(pos_control_result, neg_control_result, aliquots)
				self.add_pcr(pcr)
			for line in f:
				[error, r_tag, manufacturer, prob] = line.split()
				self.error_probs[(error, REVERSE_REAGENT_MAP[r_tag], manufacturer)] = float(prob)
		
	def get_error_prob(self, aliquot, error):
		if (error, aliquot.reagent, aliquot.manufacturer) in self.error_probs:
			return self.error_probs[(error, aliquot.reagent, aliquot.manufacturer)]
		elif error == 'defective':
			return 0.1
		elif error == 'contaminated':
			return 0.1
	
	def parse_reagent_line(self, words, all_aliquots):
		reagent = REVERSE_REAGENT_MAP[words[0]]
		id = words[1]
		manufacturer = words[2]
		new_aliquot = Aliquot(reagent, id, manufacturer)
		for aliquot in all_aliquots:
			if aliquot.is_same_aliquot(new_aliquot):
				return aliquot
		all_aliquots.append(new_aliquot)
		return new_aliquot
	
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
	
