# -*- coding: utf-8 -*-

from pcrclasses import *
import copy
import sys
import itertools

class PCRLogic:
	def __init__(self, pcr_database):
		self.pcr_database = pcr_database
    
	"""
	Right now, this function returns a list of possible culprit aliquots.
	In the future, it could return (culprit, probability) pairs, or otherwise convey more
	information.
	"""
	def make_deductions(self, pcr):
		if pcr.had_defective_reagent():
			possible_defective_aliquots = self.find_defective_aliquots(pcr)
			if len(possible_defective_aliquots) == 0:
				raise Exception('Could not find defective reagent in PCR with false negative.')
			return possible_defective_aliquots
		if pcr.had_contaminated_reagent():
			possible_contaminated_aliquots = self.find_contaminated_aliquots(pcr)
			if len(possible_contaminated_aliquots) == 0:
				raise Exception('Could not find defective reagent in PCR with false positive.')
			return possible_contaminated_aliquots
		# If this PCR was neither a false positive nor a false negative, 
		# return an empty list.  Nothing is wrong.
		return list()

	def make_probabilistic_deductions(self):
		database = self.pcr_database
		pcrs = database.pcrs
		aliquots = list()
		for pcr in pcrs:
			aliquots.extend(pcr.aliquots)
		aliquots = set(aliquots)
		prune_nondefective(aliquots, pcrs)
		aliquots = list(aliquots)
		assignments = [tup for tup in itertools.product([False, True], repeat = len(aliquots))]
		assignment_map = {}
		for assignment in assignments:
			assignment_map[assignment] = process_assignment(assignment, aliquots, pcrs)

	def prune_nondefective(aliquots, pcrs):
		nondefectives = [pcr in pcrs if not pcr.had_defective_reagent()]
		for pcr in nondefectives:
			aliquots.remove(set(pcr.aliquots))

	def process_assignment(assignment, aliquots, pcrs):
		prob = 1.0
		for i in range(len(assignment)):
			prob *= get_defective_prob(i, aliquots) if assignment[i] else 1 - get_defective_prob(i, aliquots)
		defective_aliquots = set([aliquots[i] for i in range(len(assignment)) if assignment[i]])
		for pcr in pcrs:
			if pcr.had_defective_reagent():
				pcr_aliquots = set(pcr.aliquots)
				if len(defective_aliquots.intersection(pcr_aliquots)) == 0:
					return (prob, False)
		return (prob, True)



	def get_defective_prob(index, aliquots):
		return 0.5
	
	def find_defective_aliquots(self, pcr):
		# Start out with all the aliquots as defective candidates
		possible_defective_aliquots = copy.deepcopy(pcr.aliquots)
		for aliquot in pcr.aliquots:
			# Find all the PCRs that used this same aliquot of this reagent 
			pcrs = self.pcr_database.pcrs_with_aliquot(aliquot)
			for pcr in pcrs:
				"""
				If we had an instance of a PCR with this aliquot that was not a false negative, 
				we know this aliquot is reactive (not defective).  Even if the PCR had a false 
				positive (meaning another reagent in that PCR had contamination), we can rule 
				out THIS aliquot as not defective.
				"""
				if not pcr.had_defective_reagent():
					self.remove_aliquot_from_candidates(possible_defective_aliquots, aliquot)
					break
		return possible_defective_aliquots
	
	def find_contaminated_aliquots(self, pcr):
		# Start out with all the aliquots as contamination candidates
		possible_contaminated_aliquots = copy.deepcopy(pcr.aliquots)
		
		for aliquot in pcr.aliquots:
			# Find all the PCRs that used this same aliquot of this reagent 
			pcrs = self.pcr_database.pcrs_with_aliquot(aliquot)
			for pcr in pcrs:
				"""
				To rule out a reagent as contaminated, there must have been a SUCCESSFUL PCR
				completed (i.e. it didn't have any defective reagents; the positive control was 
				positive) and that PCR cannot have had a negative control give a positive result.
				"""
				if not pcr.had_defective_reagent() and not pcr.had_contaminated_reagent():
					self.remove_aliquot_from_candidates(possible_contaminated_aliquots, aliquot)
					break
		return possible_contaminated_aliquots
					
	def remove_aliquot_from_candidates(self, candidates, aliquot):
		for other in candidates:
			if aliquot.is_same_aliquot(other):
				candidates.remove(other)
			
	
