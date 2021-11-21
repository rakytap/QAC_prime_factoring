# test file for the integer prime factorization

import abstract_binary.base as abs_bin_base
from abstract_binary.binary_number import bin_num
from abstract_binary.abstract_binary_number import abstract_bin_num
import abstract_binary.multiply
from abstract_binary.multiply import multiplication_table
import compose_BQM.compose_BQM
from compose_BQM.compose_BQM import BQM_from_multiplication_table


# Setting DEBUG variables
abstract_binary.multiply.DEBUG = True
compose_BQM.compose_BQM.DEBUG = True

#test for the multiplication table

# The bitlengths of the binary numbers
bitnum1 = 8
bitnum2 = 4

# The abstract representattion of the binary numbers
abs_num_1 = abstract_bin_num(bitnum1)
abs_num_2 = abstract_bin_num(bitnum2)



# cerating class of the multiplication table
pq = multiplication_table(abs_num_1, abs_num_2)

# determine the block sizes in the multiplcation table
pq.determine_blocks(2)


for col in range(0, bitnum1+bitnum2):
	pq.get_column_BQM_dict( col )


#######################################
# test for multiplication 11x13=143

# the target number
target = 13*19#143

# creating the represantation of the target number
target_num = bin_num( target )
print( 'bit length of the target number: ' + str(target_num.bit_length()) )

# creating the skeleton of the unknows factors
num1 = abstract_bin_num(5)
num2 = abstract_bin_num(5)

# the first and last bit should be 1
#num1.set_bit(0,1)
#num2.set_bit(0,1)
#num1.set_bit(3,1)
#num2.set_bit(3,1)


# create a class to construct the BQM from the multiplication table
cBQM = BQM_from_multiplication_table(num1, num2, target_num)

# generating the blocks
cBQM.determine_blocks(2)


# sum up the quadratic terms in a given block >= 0
#block = 1
#cBQM.sum_up_block(block)

# generate the (pq-**2 cost function for a given block
cBQM.cost_function_of_block(0)
update_cost_function = True
cBQM.cost_function_of_block(1, update_cost_function)
cBQM.cost_function_of_block(2, update_cost_function)
cBQM.cost_function_of_block(3, update_cost_function)
cBQM.cost_function_of_block(4, update_cost_function)

# adding the substitution penalty functions to the (pq-n)**2 cost function
cBQM.add_penalties_to_cost_function()

# the binary representation of the targer number:
print(' ')
print('The target number: ' + str(target) +' = (' + str(bin(target)) + ')')

# retrive the cost function and the constant term
(BQM_model, constant) = cBQM.get_cost_function()

##################################################
# Solving by QBsolv
print('************************')
print( 'Solving by QBsolv' )
from dwave_qbsolv import QBSolv

# the response of QBsolve
response = QBSolv().sample_qubo(BQM_model)
print("samples=" + str(list(response.samples())))
print("energies=" + str(list(response.data_vectors['energy'])))


# obatin the QBsolv's result
smpls = response.samples()
res = dict( smpls[0] ) # the result of the lowest energy
print(' ')
print( 'The result of the QBsolv:')
print(res)


# Checking the substitutions
print(' ')
print('Checking the substitutions')
substitutions = cBQM.get_substitutions()
for item in substitutions.items():
	vars = item[0]
	subs_var_value = res[vars[0]]*res[vars[1]]
	if subs_var_value == res[item[1]]:
		print(str(vars[0]) + '*' + str(vars[1]) + '==' + str(item[1]) + ':  Passed')
	else:
		print(str(vars[0]) + '*' + str(vars[1]) + '==' + str(item[1]) + ': Failed')
print(' ')

# Check the energy of the result: the cost function including the constant part should be zero
energies = response.data_vectors['energy']
if energies[0] + constant == 0:
	print( 'The lowest energy solution is: ' + str(energies[0]) )
else:
	print( 'Energy test failed!' )

# retriving the decimal form of the factors

# get the bit labels of the abstract binary numbers
bit_labels_num1 = num1.get_bit_labels()
bit_labels_num2 = num2.get_bit_labels()


for bit in range(num1.bit_length()):
	bit_label = bit_labels_num1[bit]
	if bit_label in res.keys():
		num1.set_bit( bit, res[bit_label] )

for bit in range(num2.bit_length()):
	bit_label = bit_labels_num2[bit]
	if bit_label in res.keys():
		num2.set_bit( bit, res[bit_label] )



print(num1.get_decimal())
print(num2.get_decimal())

#num1.define_bit(0,1)
#num2.define_bit(0,1)
#num1.define_bit(3,1)
#num2.define_bit(3,1)


