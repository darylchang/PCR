#!/usr/bin/python

import random, sys
from pcrlogic import PCRLogic
from pcrclasses import *
"""
TODO (maesen): This test suite could use a lot of beefing up.  
"""


def main():
	test_illegal_pcr()
	test_perfect_pcr()
	test_no_deduction_possible()
	test_basic_contamination()
	test_basic_defective()
	test_probabilistic_deductions_defective()
	test_probabilistic_deductions_contaminated()
	simulate_pcrs(100)

"""
In this test case, we have one perfect PCR in our database.  We want to make deductions
about a PCR with a negative positive-control result (i.e. defective reagent).
We confirm that aliquots with overlap in the perfect PCR are eliminated as suspects.
 
"""
def test_basic_defective():
	db = PCRDatabase()
	primer1 = Aliquot(PRIMER, '1', 'Biowares')
	taq1 = Aliquot(TAQ, '1', 'Biowares')
	dntp1 = Aliquot(DNTP, '1', 'Biowares')
	buffer1 = Aliquot(BUFFER, '1', 'Biowares')
	pcr = PCR(True, False, [primer1, taq1, dntp1, buffer1])
	db.add_pcr(pcr)
	logic = PCRLogic(db)
	buffer2 = Aliquot(BUFFER, '2', 'Biowares')
	taq2 = Aliquot(TAQ, '2', 'Biowares')
	pcr2 = PCR(False, False, [primer1, taq2, dntp1, buffer2])
	possible_culprits = logic.make_deductions(pcr2)
	if len(possible_culprits) == 2 and possible_culprits[0].id == '2' and possible_culprits[1].id == '2':
		print 'Basic defective test successful!'
	else:
		print 'Basic defective test FAILED!'
"""
In this test case, we have one perfect PCR in our database.  We want to make 
deductions about a PCR with a positive negative-control result (i.e. contamination).
We confirm that the aliquots that overlap with the perfect PCR are eliminated as 
suspects.
"""
def test_basic_contamination():
	db = PCRDatabase()
	primer1 = Aliquot(PRIMER, '1', 'Biowares')
	taq1 = Aliquot(TAQ, '1', 'Biowares')
	dntp1 = Aliquot(DNTP, '1', 'Biowares')
	buffer1 = Aliquot(BUFFER, '1', 'Biowares')
	pcr = PCR(True, False, [primer1, taq1, dntp1, buffer1])
	db.add_pcr(pcr)
	logic = PCRLogic(db)
	buffer2 = Aliquot(BUFFER, '2', 'Biowares')
	taq2 = Aliquot(TAQ, '2', 'Biowares')
	pcr2 = PCR(True, True, [primer1, taq2, dntp1, buffer2])
	possible_culprits = logic.make_deductions(pcr2)
	if len(possible_culprits) == 2 and possible_culprits[0].id == '2' and possible_culprits[1].id == '2':
		print 'Basic contamination test successful!'
	else:
		print 'Basic contamination test FAILED!'

"""
In this test, we attempt to construct a PCR where the positive control had a negative
result, and the negative control had a positive result.  Since we make the assumption that
a negative result on a positive control means at least one reagent is defective, and therefore
ALL PCRs with the same aliquot of that reagent will have negative results (even if they also
contain contaminated reagents), we throw an exception here.  We don't let the client construct
these (really screwed up) PCRs, since these results would mean more than just reagents 
have gone wrong in the PCR.
"""	
def test_illegal_pcr():
	try:
		pcr = PCR(False, True, [])
		print 'Illegal PCR test FAILED!'
	except:
		print 'Illegal PCR test successful!'

	
"""
In this test, we add one PCR to our database that had a successful result.  We then
attempt to make a deduction about another PCR using THE SAME aliquots of reagents, 
where the PCR had a false positive control.  Since we haven't built in any notion of 
reagent status change over time, this should throw an error.
"""
def test_no_deduction_possible():
	db = PCRDatabase()
	primer1 = Aliquot(PRIMER, '1', 'Biowares')
	taq1 = Aliquot(TAQ, '1', 'Biowares')
	dntp1 = Aliquot(DNTP, '1', 'Biowares')
	buffer1 = Aliquot(BUFFER, '1', 'Biowares')
	pcr = PCR(True, False, [primer1, taq1, dntp1, buffer1])
	db.add_pcr(pcr)
	logic = PCRLogic(db)
	pcr2 = PCR(False, False, [primer1, taq1, dntp1, buffer1])
	try:
		logic.make_deductions(pcr2)
		print 'No deduction possible test FAILED!'
	except:
		print 'No deduction possible test successful!'


"""
This tests a perfect PCR (negative control had a negative result, positive
control had a positive result).  
"""
def test_perfect_pcr():
	db = PCRDatabase()
	logic = PCRLogic(db)
	primer1 = Aliquot(PRIMER, '1', 'Biowares')
	taq1 = Aliquot(TAQ, '1', 'Biowares')
	dntp1 = Aliquot(DNTP, '1', 'Biowares')
	buffer1 = Aliquot(BUFFER, '1', 'Biowares')
	pcr = PCR(True, False, [primer1, taq1, dntp1, buffer1])
	culprits = logic.make_deductions(pcr)
	if(len(culprits) == 0):
		print 'Perfect PCR test successful!'
	else:
		print 'Perfect PCR test FAILED!'
	
"""
This tests the probabilistic PSM in PCRLogic.
"""
def test_probabilistic_deductions_defective():
	db = PCRDatabase()
	primer1 = Aliquot(PRIMER, '1', 'Biowares')
	taq1 = Aliquot(TAQ, '1', 'Biowares')
	dntp1 = Aliquot(DNTP, '1', 'Biowares')
	buffer1 = Aliquot(BUFFER, '1', 'Biowares')
	pcr = PCR(False, False, [primer1, taq1, dntp1, buffer1])
	db.add_pcr(pcr)

	buffer2 = Aliquot(BUFFER, '2', 'Biowares')
	pcr2 = PCR(False, False, [primer1, taq1, dntp1, buffer2])
	db.add_pcr(pcr2)

	buffer3 = Aliquot(BUFFER, '3', 'Biowares')
	pcr3 = PCR(False, False, [primer1, taq1, dntp1, buffer3])
	db.add_pcr(pcr3)

	buffer4 = Aliquot(BUFFER, '4', 'Biowares')
	pcr4 = PCR(False, False, [primer1, taq1, dntp1, buffer4])
	db.add_pcr(pcr4)

	logic = PCRLogic(db)
	possible_culprits = logic.make_probabilistic_deductions()
	print possible_culprits

"""
This tests the probabilistic PSM in PCRLogic.
"""
def test_probabilistic_deductions_contaminated():
	db = PCRDatabase()
	primer1 = Aliquot(PRIMER, '1', 'Biowares')
	taq1 = Aliquot(TAQ, '1', 'Biowares')
	dntp1 = Aliquot(DNTP, '1', 'Biowares')
	buffer1 = Aliquot(BUFFER, '1', 'Biowares')
	pcr = PCR(True, True, [primer1, taq1, dntp1, buffer1])
	db.add_pcr(pcr)

	buffer2 = Aliquot(BUFFER, '2', 'Biowares')
	pcr2 = PCR(True, True, [primer1, taq1, dntp1, buffer2])
	db.add_pcr(pcr2)

	buffer3 = Aliquot(BUFFER, '3', 'Biowares')
	pcr3 = PCR(True, True, [primer1, taq1, dntp1, buffer3])
	db.add_pcr(pcr3)

	buffer4 = Aliquot(BUFFER, '4', 'Biowares')
	pcr4 = PCR(True, True, [primer1, taq1, dntp1, buffer4])
	db.add_pcr(pcr4)

	logic = PCRLogic(db)
	possible_culprits = logic.make_probabilistic_deductions()
	print possible_culprits

"""
Simulates PCRs and evaluates cost.
"""
def simulate_pcrs(num_pcrs):
    db = PCRDatabase()
    logic = PCRLogic(db)
    state_probabilities = {'contaminated': 0.05, 'defective': 0.05, 'good': 0.9}
    curr_aliquots = [Aliquot(reagent, 1, 'Biowares', choose(state_probabilities)) for reagent in REAGENT_MAP]

    for i in range(num_pcrs):
        false_neg = any(map(lambda aliquot: aliquot.state == 'defective', curr_aliquots))
        false_pos = any(map(lambda aliquot: aliquot.state == 'contaminated', curr_aliquots)) and not false_neg
        if false_neg:
            pcr = PCR(False, False, curr_aliquots)
        elif false_pos:
            pcr = PCR(True, True, curr_aliquots)
        else:
            pcr = PCR(True, False, curr_aliquots)
        db.add_pcr(pcr)
        curr_aliquots = [random.choice([aliquot, Aliquot(aliquot.reagent, aliquot.id+1, aliquot.manufacturer, random.choice(['c', 'd', 'g']))]) \
                        for aliquot in curr_aliquots]
        # defective_aliquots = set(filter(lambda x:x>0.1, logic.make_probabilistic_deductions()['defective']))
        # contaminated_aliquots = filter(lambda x:x>0.1, logic.make_probabilistic_deductions()['contaminated'])
        # bad_aliquots = defective_aliquots.union(contaminated_aliquots)
        # curr_aliquots = [aliquot if aliquot not in bad_aliquots else Aliquot(aliquot.reagent, aliquot.id+1, aliquot.manufacturer, choose(state_probabilities)) \
        #                  for aliquot in curr_aliquots]

    print [(pcr.pos_control_result, pcr.negative_control_result) for pcr in db.pcrs]
    print score(db)
    
"""
TODO: 
"""
def score(db):
    percent_clean = sum([float(pcr.pos_control_result == True and pcr.negative_control_result == False) for pcr in db.pcrs]) / len(db.pcrs)
    num_aliquots = len(set([aliquot for pcr in db.pcrs for aliquot in pcr.aliquots])) / len(REAGENT_MAP)
    avg_num_aliquots = num_aliquots / len(db.pcrs)
    return (percent_clean + avg_num_aliquots) / 2
			
def choose(d):
    r = random.uniform(0, sum(d.itervalues()))
    s = 0.0
    for k, w in d.iteritems():
        s += w
        if r < s: return k
    return k
    
if __name__ == "__main__":
    main()

