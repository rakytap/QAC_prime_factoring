# test file for the integer prime factorization

import abstract_binary.base as abs_bin_base
from abstract_binary.binary_number import bin_num
from abstract_binary.abstract_binary_number import abstract_bin_num
import abstract_binary.multiply
from abstract_binary.multiply import multiplication_table
import compose_BQM.compose_BQM
from compose_BQM.compose_BQM import BQM_from_multiplication_table
import factorization.iterative 
from factorization.iterative import iterative_factorization


# Setting DEBUG variables
abstract_binary.multiply.DEBUG = False
compose_BQM.compose_BQM.DEBUG = False
factorization.iterative.DEBUG = False



# the target number
target = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139



# creating the represantation of the target number
target_num = bin_num( target )
print( 'bit length of the target number: ' + str(target_num.bit_length()) )

# binary representation of the factors
fact1 = 37975227936943673922808872755445627854565536638199
fact2 = 40094690950920881030683735292761468389214899724061
fact1_bin = bin_num( fact1 )
fact2_bin = bin_num( fact2 )


# creating the skeleton of the unknows factors
num1 = abstract_bin_num(50)
num2 = abstract_bin_num(50)



# create a class to construct the BQM from the multiplication table
cIter = iterative_factorization(num1, num2, target_num)

# run the iterations to solve the factorization problem
cIter.run_iterations()



# Bits of the exact solution
print(' ')
print('Bits of the exact solution: ')
print('fact1: ' + bin(fact1) )
print('fact2: ' + bin(fact2) )




