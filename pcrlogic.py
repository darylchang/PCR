# -*- coding: utf-8 -*-

from pcrclasses import *
import copy
import sys
import itertools

PROB_INDEX = 0
FIT_INDEX = 1

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
		errors = ['defective', 'contaminated']
		results = {}
		for error in errors:
			# Create a list of aliquots that may have been bad
			pcrs = self.pcr_database.pcrs
			aliquots = self.pcr_database.get_all_aliquots()
			aliquots = list(self.prune_aliquots(aliquots, pcrs, error))

			# Create all possible aliquot assignments of defective/non-defective
			assignments = [tup for tup in itertools.product([False, True], repeat = len(aliquots))]
			assignment_map = {}
			for assignment in assignments:
				assignment_map[assignment] = self.process_assignment(assignment, aliquots, pcrs, error)
			aliquot_results = [(aliquots[i], self.get_bayesian_prob(i, assignment_map)) \
							   for i in range(len(aliquots))]
			aliquot_results.sort(key=lambda x:x[1], reverse=True)
			results[error] = aliquot_results
		return results

	def prune_aliquots(self, aliquots, pcrs, error):
		clean_pcrs = [pcr for pcr in pcrs if not pcr.had_bad_reagent(error)]
		for pcr in clean_pcrs:
			aliquots = aliquots.difference(set(pcr.aliquots))
		return aliquots
			
	def process_assignment(self, assignment, aliquots, pcrs, error):
		prob = 1.0
		for i in range(len(assignment)):
			prob *= self.get_error_prob(i, aliquots, error) if assignment[i] else 1 - self.get_error_prob(i, aliquots, error)
		bad_aliquots = set([aliquots[i] for i in range(len(assignment)) if assignment[i]])
		bad_pcrs_aliquots = [set(pcr.aliquots) for pcr in pcrs if pcr.had_bad_reagent(error)]
		for bad_pcr_aliquots in bad_pcrs_aliquots:
			if not bad_pcr_aliquots.intersection(bad_aliquots):
				return (prob, False)
		return (prob, True)

	def get_bayesian_prob(self, aliquot_index, assignment_map):
		temp_list = [assignment_map[assign] for assign in assignment_map if assign[aliquot_index]]
		prob_results_given_error = sum([tup[PROB_INDEX] for tup in temp_list if tup[FIT_INDEX]])
		temp_list = [assignment_map[assign] for assign in assignment_map if not assign[aliquot_index]]
		prob_results_given_fine = sum([tup[PROB_INDEX] for tup in temp_list if tup[FIT_INDEX]])
		return prob_results_given_error / (prob_results_given_error + prob_results_given_fine)

	"""
	TODO: Take into account the manufacturer of the aliquot here?
	"""
	def get_error_prob(self, index, aliquots, error):
		return self.pcr_database.get_error_prob(aliquots[index], error)
	
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
			
	
