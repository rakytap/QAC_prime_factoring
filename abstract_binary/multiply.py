from .base import *
from .abstract_binary_number import *



##
# @brief Class to access the multiplication table of two abstract binary numbers represented by class abstract_bin_num. The bit length of _p is always greater than the bit length of _q.
class multiplication_table():


	##
	# @brief Constructor of the class. Values num1 and num2 are stores by class attributes _p and _q such that bit_length(_p) >= bit_length(_q)
	# @param num1 The first abstract binary number (an instance of class abstract_bin_num)
	# @param num2 The second abstract binary number (an instance of class abstract_bin_num)
	def __init__( self, num1, num2 ):

		# The list of block separators (i.e. the list of the last columns of each block in the multiplication table)
		self._block_list = list()
		# The dictionary of columns containing carry bits
		self._carry_col_dict = dict()
		## The first abstract binary number to be multiplied
		self._p = None
		## The second abstract binary number to be multiplied
		self._q = None
	
		# test the types of the input parameters
		if not isinstance(num1, abstract_bin_num):
			raise Exception('p is not valid input type')
			
		if not isinstance(num2, abstract_bin_num):
			raise Exception('q is not valid input type')
			
		
		if num1.bit_length() >= num2.bit_length() :
			self._p = num1
			self._q = num2
		else:
			self._p = num2
			self._q = num1

		# setting the bit labels of the abstract numbers
		for bit in range(0,self._p.bit_length()):
			self._p.set_bit_label( bit, 'p' + str(bit) )
		

		for bit in range(0,self._q.bit_length()):
			self._q.set_bit_label( bit, 'q' + str(bit) )

	##
	# @brief Gets the abstarct binary numbers q and p
	# @return Returns with a tuple of the abstract binary numbers (p,q)
	def get_abstract_nums( self):	
		return (self._p, self._q)
		#TODO rather a copy of the numbers shpuld be returned


	##
	# @brief Determines the column-blocks in the multiplication table (see Table 1 and 2 in arXiv:1804.02733)
	# @param col The index labeling column. col >=0
	# @return Returns with the key representing the carry of the column or its value when it is known. (If there is no carry in the column, None is returned)
	def get_carry( self, col):	
		# test whether the blocks are already constructed
		if len( self._carry_col_dict ) == 0:
			raise('Firt construct the blocks by method multiplication_table.determine_blocks')

		if col in self._carry_col_dict.keys():
			return self._carry_col_dict[col]
		else:
			return None
		
			
	##
	# @brief Determines the column-blocks in the multiplication table (see Table 1 and 2 in arXiv:1804.02733)
	# @param max_block_size The maximal block size
	# @return Returns with the list of block separators. (i.e. the list of the last columns of each block in the multiplication table)
	def determine_blocks( self, max_block_size):
		# The firs block contains only the first column labeled by 2^0
		self._block_list.append( 0 )
		
		col = 1
		max_col = self._p.bit_length() + self._q.bit_length() - 1
		#print('max_col = ' + str(max_col))
		
		power = 0
		max_block_carry = 0
		min_next_block_size = max_block_size
		while col <= max_col:
			
			if col < self._q.bit_length():
				max_carry = col+1
			elif col < self._p.bit_length():
				max_carry = self._q.bit_length()
			else:
				max_carry = self._p.bit_length() + self._q.bit_length() - col - 1
				
			if DEBUG:
				print('max carry in col ' + str(col) + ':  ' + str(max_carry))	
			
			if (max_block_carry + max_carry*(2**power)).bit_length() > power+1+max_block_size :									
				self._block_list.append( col-1 )	
				min_next_block_size = max_block_carry.bit_length() - power - 1 	
				
				# determine the carries for the next block
				for carry_col_idx in range(col, col+min_next_block_size-1):
					self._carry_col_dict[carry_col_idx] = 'c' + str(carry_col_idx)
							
				
				power = 1				
				max_block_carry = max_carry
				
			elif power+1 > max_block_size:
				self._block_list.append( col-1 )	
				min_next_block_size = max_block_carry.bit_length() - max_block_size
				
				# determine the carries for the next block
				for carry_col_idx in range(col, col+min_next_block_size):
					self._carry_col_dict[carry_col_idx] = 'c' + str(carry_col_idx)
				
				power = 1				
				max_block_carry = max_carry
				
			else:
				max_block_carry = max_block_carry + max_carry*(2**power)
				power = power+1
				
		
			if min_next_block_size > max_block_size:
				raise('The given maximal block size is insufficient because overlap in the carries appears.')
			
			col = col + 1


		# append the last column to terminate the blocks
		self._block_list.append( self._p.bit_length() + self._q.bit_length() - 1 ) # the columns starts with 0
		
		if DEBUG:		
			print()
			print('The list of the block separators')
			print( self._block_list )
		
			print()
			print('The list of the carry bits')
			print( self._carry_col_dict )
	
	
		
	##
	# @brief Gets the 0<=col-th column of the multiplication table in form a BQM (https://docs.ocean.dwavesys.com/en/latest/docs_dimod/reference/bqm/binary_quadratic_model.html) described by a dictionary
	# @param col The index labeling column. col >=0
	# @param power Weight the values of the resulted dictionary by 2**power. Usefull when summin up an entire block into a BQM (for default power=0)
	# @return Returns with a dictionary describing the BQM model of the multiplication table, without the carries.
	def get_column_BQM_dict( self, col, power=0):
		
		#check the value of the input col
		if col >= self._p.bit_length() + self._q.bit_length():
			raise Exception('col should be less than the sum of the bit numbers of p and q')
		
		# determine the bit indices involved in the ith column of the multiplication table
		if col == 0:
			p_indexes = list(range(0,1))
			q_indexes = list(range(0,1))
		elif col < self._q.bit_length():
			p_indexes = list(range(0, col+1))
			q_indexes = list(range(col, -1, -1))
		elif col < self._p.bit_length():
			p_indexes = list(range(col-self._q.bit_length()+1, col+1))
			q_indexes = list(range(self._q.bit_length()-1, -1, -1))
		else:
			p_indexes = list(range(col-self._q.bit_length()+1, self._p.bit_length()))
			q_indexes = list(range(self._q.bit_length()-1, col-self._p.bit_length(), -1))
			
		
		# generating the BQM representing the ith column of the multiplication table (without carries)
		# quadratic terms
		quadratic = dict()
		# linear terms
		linear = dict()
		# constant
		constant = 0
		
		weight = 2**power
		for idx in range(0, len(p_indexes)):			
			if self._p.check_bit(p_indexes[idx]) and self._q.check_bit(q_indexes[idx]) :
				if self._p.get_bit(p_indexes[idx]) and self._q.get_bit(q_indexes[idx]) :
					constant = constant + weight
			elif self._p.check_bit(p_indexes[idx]) :
				linear[ 'q'+str(q_indexes[idx]) ] = self._p.get_bit(p_indexes[idx])*weight
			elif self._q.check_bit(q_indexes[idx]) :
				linear[ 'p'+str(p_indexes[idx]) ] = self._q.get_bit(q_indexes[idx])*weight
			else :
				quadratic[ ('p'+str(p_indexes[idx]), 'q'+str(q_indexes[idx]) ) ] = weight
				
				
		# combining the quadratic, linear and constant terms
		BQM_dict = dict();
		BQM_dict.update( quadratic )
		BQM_dict.update( linear )
		BQM_dict['constant'] = constant

		if DEBUG:			
			print()
			print( 'The BQM model of the ' + str(col) + 'th column' )
			for item in BQM_dict.items():
				print( item )	
					
		
		return BQM_dict
