from abstract_binary.multiply import multiplication_table
from abstract_binary.binary_number import bin_num
from dwave_qbsolv import QBSolv

from abstract_binary.abstract_binary_number import abstract_bin_num

# Set True to show debug information, or False otherwise
DEBUG = False


# String in the dictionaries labeling a constant value
CONST = 'constant'

# String in the dictionaries labeling carry bits
CARRY = 'carry'

##
# @brief Class to reduce the higher order terms in binary polinomials via a substitutional method of <a href="https://docs.dwavesys.com/docs/latest/c_handbook_3.html#non-quadratic-higher-degree-polynomials-to-ising-qubo">DWave dimod</a>
# @description The substituted variables x_k = x_i*y_j are stored in a dictionary with a penalty function. This class might be used to reduce the polinomial orders while the BQM model is under construction. Thus this solution might be faster than the post processing solution of the Dwave API, and the data produced during the reduction are also accessible.
class iterative_factorization( multiplication_table ):



	##
	# @brief Constructor of the class. Values num1 and num2 are stores by class attributes _p and _q such that bit_length(_p) >= bit_length(_q)
	# @param num1 The first abstract binary number (an instance of class abstract_bin_num)
	# @param num2 The second abstract binary number (an instance of class abstract_bin_num)
	def __init__( self, num1, num2, target_num ):
		multiplication_table.__init__(self, num1, num2)

		# The number to be factorized given as an instance of class abstract_binary.binary_number.bin_num
		self._target_num = target_num
		# The default size of the blocks in the multiplication table
		self._block_size = 5
		# The number of blocks in the multiplication table
		self._total_block_num = None
		# The list of exact solutions in the iteration process (The first bit is assumed to be 1 for odd numbers)
		self._exact_solutions = list()
		self._exact_solutions.append({'p': '1', 'q': '1' , CARRY:'0'*self._block_size})


	##
	# @brief Iterations to solve the factorization problem
	def run_iterations(self):

		# generating the blocks
		self.determine_blocks( self._block_size )


		#The total number of blocks in the multiplication table
		self._total_block_num = len(self._block_list)

		if DEBUG:
			print('The number of blocks: ' + str(self._total_block_num) )


		# run the iterations for the blocks
		for block_id in range(1, self._total_block_num+1):
			
			if DEBUG:
				print('Starting iteration ' + str(block_id) )

			# determine the exact solution for one block
			exact_solutions = list()
			for previous_idx in range(0, len(self._exact_solutions) ): #the new solutions are determined in terms of the previous solutions
				new_exact_solutions = self.run_iteration(block_id, self._exact_solutions[previous_idx])
				exact_solutions = exact_solutions + new_exact_solutions	

			self._exact_solutions = exact_solutions

			print('number of exact solutions: ' + str(len(self._exact_solutions)))
			if DEBUG:				
				print('Exact solustions: ')
				print( self._exact_solutions )




	##
	# @brief Add another bits to the exact solution stored in the self._exact_solutions
	# @param exact_solution The list of new exact solutions in form {p:binary_format, q:binary_format, CARRY:binary_format}
	def add_block_to_exact_solutions(self, block_id):
		pass


	##
	# @brief Run one iteration in the solving process
	# @param block_id The id = 0,1,2,3,... of the block
	# @return Returns with a list of the exact solutions and with the carry bits for the next block of form {p:binary_format, q:binary_format, CARRY:binary_format}
	def run_iteration(self, block_id, previous_solutions=None):
		
		#print(previous_solutions)
		#setting the already known bits from the list of exact solutions
		for bit_idx in range(0, len(previous_solutions['p']) ): 
			self._p.set_bit( 0, int(previous_solutions['p'][bit_idx]) )

		for bit_idx in range(0, len(previous_solutions['q']) ): 
			self._q.set_bit( 0, int(previous_solutions['q'][bit_idx]) )


		# The new bits of the number involved in the current block (and not involved in the previous blocks)
		p_bits = list( range(self._block_list[block_id-1]+1, self._block_list[block_id]+1) )
		q_bits = list( range(self._block_list[block_id-1]+1, self._block_list[block_id]+1) )
		

		# define the range of the numbers p and q
		max_p = 0
		for idx in range(0, len(p_bits)):
			max_p = max_p + 2**idx


		max_q = 0
		for idx in range(0, len(q_bits)):
			max_q = max_q+ 2**idx

		


		exact_solutions = list()
		# the iteration to find the exact solutions
		for p_idx in range(1,max_p+1):
			p_bin = ('{0:0'+str(len(p_bits))+'b}').format(p_idx)

			# set the bits of the abstract binary number _q
			for bit_idx in range(p_bits[0], p_bits[len(p_bits)-1]+1):
				self._p.set_bit( bit_idx, int(p_bin[-(bit_idx-p_bits[0]+1)]) )

			
			for q_idx in range(1, p_idx+1):
				q_bin = ('{0:0'+str(len(q_bits))+'b}').format(q_idx)

				# set the bits of the abstract binary number _q
				for bit_idx in range(q_bits[0], q_bits[len(q_bits)-1]+1):
					self._q.set_bit( bit_idx, int(q_bin[-(bit_idx-q_bits[0]+1)]) )
	
				block_BQM = self.sum_up_block( block_id )

				# determine the last 2*_block_size bits of the constant in the BQM of the block
				constant = block_BQM[CONST]

				# adding the carry to the constant
				constant = constant + self.bin_to_dec(previous_solutions[CARRY])
				constant = ('{0:0'+str(2*self._block_size)+'b}').format(constant)
				if constant[self._block_size:2*self._block_size] == '0'*self._block_size:  # compare the last _block_size bits of the constant to zero
					# found an exact solution

					# determine the carry bits
					carry_bits = constant[0:self._block_size] 
					
					# append the exact solution to the list of exact solutions
					exact_solutions.append( {'p':p_bin + previous_solutions['p'], 'q':q_bin + previous_solutions['q'], CARRY:carry_bits} )

		





		return exact_solutions
						

		# The number of exact solutions
		print('The number of exact solutions: ' + str(len(exact_solutions)) )


	##
	# @brief Convert a binary format to a decimal number
	# @param bin_format ....
	# @return Returns with the decimal value
	def bin_to_dec( self, bin_format):
		dec_val = 0
		power = 1
		for idx in range(0, len(bin_format)):
			dec_val = dec_val + int(bin_format[-idx-1])*power
			power = power*2
	
		return dec_val
		

	##
	# @brief Sums up a block of the multiplication number
	# @param block_id >= 0 The number identificating the corresponding block
	# @return Returns with a dictionary of the BQM model: ( (x_i, x_j) : value )
	def sum_up_block( self, block_id ):
		# test whether the blocks are already constructed
		if len( self._block_list ) == 0:
			raise('Firt construct the blocks by method multiplication_table.determine_blocks')

		# test the validity of the given block
		block_num = len( self._block_list )
		if block_id > block_num:
			raise('There are less blocks than given be the parameter block_id')

		# determine the columns in the block
		cols = list()
		if block_id == 0:
			cols.append(0)
		else:
			for col_tmp in range( self._block_list[block_id-1]+1, self._block_list[block_id]+1 ):
				cols.append(col_tmp)

		if DEBUG:
			print('\nThe columns involved in the block_id=' + str(block_id) + ' block: ' + str(cols))

		# now lets compose a dictionary of a BQM model of the summed block
		block_BQM_dict = dict( {CONST:0} )
		power = 0
		for col in cols:
			col_BQM_dict = self.get_column_BQM_dict(col, power)

			if DEBUG:
				print('The BQM model of the col=' + str(col) + ' :' + str(col_BQM_dict))
			
			# adding the column BQM to the block BQM
			constant = block_BQM_dict[ CONST ] #first save the constant from beeing overwritten
			block_BQM_dict.update( col_BQM_dict )
			block_BQM_dict[ CONST ] = block_BQM_dict[ CONST ] + constant

			

			# Now add the bits of the target number to the block BQM model
			target_bit = self._target_num.get_bit(col)
			if DEBUG:
				print('The target bit of col=' + str(col) + ' :' + str(target_bit)) 

			block_BQM_dict[ CONST ] = block_BQM_dict[ CONST ] - target_bit*2**power

			# increase the power for the next column
			power = power + 1


		
			

		if DEBUG:
			print('\nThe BQM model of the block=' + str(block_id) + ' :' + str(block_BQM_dict)) 

		return block_BQM_dict

		


