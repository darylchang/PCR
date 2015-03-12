#!/usr/bin/python

import math, random, sys
import string
from pcrlogic import PCRLogic
from pcrclasses import *

COMMANDS = {'0' : 'Quit', '1' : 'Read PCR Database from File', '2' : 'Add new PCR', 
	'3' : 'Detect Errors Deterministically', '4' : 'Detect Errors Probabalistically', '5' : 'Write PCR Database to File' }

def main():
	db = PCRDatabase('e2.txt')
	logic = PCRLogic(db)
	while True:
		command = get_user_command()
		if COMMANDS[command] == 'Quit': 
			break
		db, logic = process_command(command, db, logic)
		print '\n'
		
def process_command(command, db, logic):
	if command == '1':
		return read_db_command(db, logic)
	elif command == '2':
		return read_pcr_command(db, logic)
	elif command == '3':
		return deterministic_command(db, logic)
	elif command == '4':
		return probabalistic_command(db, logic)
	elif command == '5':
		return write_db_file(db, logic)
	return db, logic
	
def write_db_file(db, logic):
	filename = raw_input('What filename would you like to write to? ')
	
	f = open(filename, 'w')
	f.write(str(len(db.pcrs)) + '\n')
	f.write('\n')
	for pcr in db.pcrs:
		f.write('True\n' if pcr.pos_control_result else 'False\n')
		f.write('True\n' if pcr.negative_control_result else 'False\n')
		for aliquot in pcr.aliquots:
			f.write(REAGENT_MAP[aliquot.reagent] + '\t' + aliquot.id + '\t' + aliquot.manufacturer + '\n')
		f.write('\n')
	for (error, reagent, manufacturer) in db.error_probs:
		f.write(error + '\t' + REAGENT_MAP[reagent] + '\t' + manufacturer + '\t' + str(db.error_probs[(error, reagent, manufacturer)]) + '\n')
	
	f.close()
	
	return db, logic

def probabalistic_command(db, logic):
	results = logic.make_probabilistic_deductions()
	poss_defective_reagents = results['defective']
	poss_contaminated_reagents = results['contaminated']
	print_reagent_probs('Possible defective aliquots: ', poss_defective_reagents)
	print_reagent_probs('Possible contaminated aliquots: ', poss_contaminated_reagents)
	return db, logic
	
def print_reagent_probs(prompt, aliquots):
	print prompt
	for (aliquot, prob) in aliquots:
		print REAGENT_MAP[aliquot.reagent] + '\t' + aliquot.id + '\t' + aliquot.manufacturer + '\t' + str(prob)
	
def deterministic_command(db, logic):
	poss_defective_reagents, poss_contaminated_reagents = logic.make_deterministic_deductions()
	print_reagents('Possible defective aliquots: ', poss_defective_reagents)
	print_reagents('Possible contaminated aliquots: ', poss_contaminated_reagents)
	return db, logic
	
def print_reagents(prompt, aliquots):
	print prompt
	for aliquot in aliquots:
		print REAGENT_MAP[aliquot.reagent] + '\t' + aliquot.id + '\t' + aliquot.manufacturer
	
def read_pcr_command(db, logic):
	pos_control_result = get_yes_no('Did your positive control have a positive result? ')
	neg_control_result = not get_yes_no('Did your negative control have a negative result? ')
	print 'Begin adding aliquots to this experiment now:'
	aliquots = list()
	while get_yes_no('Are there more aliquots used in this experiment? '):
		reagent = get_reagent()
		aliquot = raw_input('Aliquot ID: ').strip()
		manu = raw_input('Manufacturer :').strip()
		aliquots.append(Aliquot(reagent, aliquot, manu))
	pcr = PCR(pos_control_result, neg_control_result, aliquots)
	db.add_pcr(pcr)
	return db, logic

def get_reagent():
	print 'Please enter one of the following reagents: '
	for key in REVERSE_REAGENT_MAP.keys():
		print key
	resp = raw_input('Reagent: ').strip().upper()
	while resp not in REVERSE_REAGENT_MAP.keys():
		print 'Please enter one of the following reagents: '
		for key in REVERSE_REAGENT_MAP.keys():
			print key
		resp = raw_input('Reagent: ').strip().upper()	
	return REVERSE_REAGENT_MAP[resp]
	
def read_db_command(db, logic):
	try:
		filename = raw_input('Enter filename: ')
		db = PCRDatabase(filename)
		logic = PCRLogic(db)
		return db, logic
	except:
		print 'Could not open that file.'
		return db, logic
		
def get_yes_no(prompt):
	resp = raw_input(prompt).strip().lower()
	while not(resp == 'y' or resp == 'n'):
		print 'Please enter "y" or "n"'
		resp = raw_input(prompt).strip().lower()
	return resp == 'y'
	
def get_user_command():
	keys = list(COMMANDS.keys())
	keys.sort()
	for num in keys:
		print num + ' : ' + COMMANDS[num]
	num = str(raw_input('Enter a command: ')).strip()
	while num not in COMMANDS.keys():
		print 'Illegal command.'
		for num in keys:
			print num + ' : ' + COMMANDS[num]
		num = str(raw_input('Enter a command: ')).strip()
	return num

if __name__ == "__main__":
    main()

