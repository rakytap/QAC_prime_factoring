from abstract_binary.multiply import multiplication_table
from abstract_binary.binary_number import bin_num


# Set True to show debug information, or False otherwise
DEBUG = False

# String in the dictionaries labeling a constant value
CONST = 'constant'

##
# @brief Class to reduce the higher order terms in binary polinomials via a substitutional method of <a href="https://docs.dwavesys.com/docs/latest/c_handbook_3.html#non-quadratic-higher-degree-polynomials-to-ising-qubo">DWave dimod</a>
# @description The substituted variables x_k = x_i*y_j are stored in a dictionary with a penalty function. This class might be used to reduce the polinomial orders while the BQM model is under construction. Thus this solution might be faster than the post processing solution of the Dwave API, and the data produced during the reduction are also accessible.
class reduce_higher_order_polynomials():

	# The automated prefix of the substituted variables. (The automatic names for the substituted variables would be 's0', 's1', 's2', etc...
	automatic_prefix = 's'


	##
	# @brief Constructor of the class.
	def __init__( self):

		# a dictionary containg (new variable: substituted variables) pairs
		self._substituted_vars = dict()
		# a dictionary containg (substituted variables: new variable) pairs
		self._substituted_values = dict()
		# a dictionary containg (new variable: panelty BQM) pairs
		self._penalties = dict()
		# The default value of the panelty amplitude
		self._penalty_amplitude = 30

	##
	# @brief Gets the default amplitude of the panelty function.
	# @return Returns with the defaunt panelty amplitude.
	def get_default_penalty_amplitude( self ):
		return self._penalty_amplitude

	##
	# @brief Gets the panelty BQMs
	# @return Returns with the dictionary of the BQM panelties of the substitutions
	def get_penalties( self ):
		return self._penalties



	##
	# @brief Creates or increase a penalty of a substitution (see Eq. (5) in arXiv:1804.02733v2). The created BQM is added to the dictionary _penalties.
	# @param subs_var A string of the variable that has been introduced as a substitution
	# @param panelty_amplitude A scalar amplitude of the panelty function
	def set_penalty( self, subs_var, panelty_amplitude=None ):

		if panelty_amplitude is None:
			panelty_amplitude = self._penalty_amplitude

		
		# check whether the new variable was already introduced or not
		if subs_var in self._substituted_vars.keys():

			substituted_pair = self._substituted_vars[ subs_var ]
			x1 = substituted_pair[0]
			x2 = substituted_pair[1]

			# check whether to create or increase the panelty
			if subs_var in self._penalties.keys():
				# retrive the existing panelty
				panelty = self._penalties[ subs_var ]

				# increase the panelty
				panelty[tuple( sorted([x1,x2])) ] = panelty[tuple( sorted([x1,x2]))] + panelty_amplitude
				panelty[tuple( sorted([x1,subs_var]))] = panelty[tuple( sorted([x1,subs_var]))] - 2*panelty_amplitude
				panelty[tuple( sorted([x2,subs_var]))] = panelty[tuple( sorted([x2,subs_var]))] - 2*panelty_amplitude
				panelty[(subs_var,subs_var)] = panelty[(subs_var,subs_var)] + 3*panelty_amplitude

				# adding the increased panelty function to the dictionary
				self._penalties[subs_var] = panelty 
				
			else:
				# creating the dictionary of the panelty function	
				panelty = dict()
				panelty[ tuple( sorted([x1,x2])) ] = panelty_amplitude
				panelty[ tuple( sorted([x1,subs_var])) ] = - 2*panelty_amplitude
				panelty[ tuple( sorted([x2,subs_var])) ] = - 2*panelty_amplitude
				panelty[(subs_var,subs_var)] = 3*panelty_amplitude
				# adding the cerated panelty function to the dictionary
				self._penalties[subs_var] = panelty 
		else:
			raise('The new variable has not yet been introduced. Use method set_substitution to create the substitution first.')
			pass


	##
	# @brief Gets the substituted variable pairs
	# @return Returns with the directory containing the substituted pairs.
	def get_substitutions( self ):
		return self._substituted_values



	##
	# @brief Gets a specific substituted variable
	# @param vars_to_substitute Two component tuple containing the strings of the variables to be substituted
	# @return Returns with a string of the substituted variable, or None if the variables of the two component list were not yet substituted.
	def get_substitution( self, vars_to_substitute ):
		if vars_to_substitute in self._substituted_values.keys():
			return self._substituted_values[vars_to_substitute]
		else:
			return None

	##
	# @brief Check whether the given product was already substituted or not?
	# @param vars_to_substitute Two component tuple containing the strings of the variables to be substituted
	# @return Returns True if the given product was already substituted, and False otherwise
	def check_substitution( self, vars_to_substitute ):
		if vars_to_substitute in self._substituted_vars.values():
			return True
		else:
			return False
		

	##
	# @brief Set a new variable z=x_i*x_j for substitution
	# @param vars_to_substitute Two component tuple containing the strings of the variables to be substituted
	# @param new_variable The name of the new variable to be set as a substitution(optional)
	# @return Returns with the name of the new variable
	def set_substitution( self, vars_to_substitute, new_variable=None ):
		# sorting the list of variables to be substituted
		vars_to_substitute = list(vars_to_substitute)
		vars_to_substitute.sort()
		vars_to_substitute = tuple(vars_to_substitute)

		if self.check_substitution( vars_to_substitute ):
			return self._substituted_values[vars_to_substitute]

		if new_variable==None:
			new_variable = self.automatic_prefix + str(len( self._substituted_vars.keys() ))
			self._substituted_vars[new_variable] = vars_to_substitute
		elif isinstance( new_variable, str):
			if new_variable in self._substituted_vars.keys():
				if self._substituted_vars[new_variable] == vars_to_substitute:
					pass
				else:
					raise('The given new_variable is already occupied')
			else:
				self._substituted_vars[new_variable] = vars_to_substitute	
		else:
			raise( 'The name of the new variable should be a string.')

		self._substituted_values[tuple(vars_to_substitute)] = new_variable
		
		
		return new_variable


##
# @brief Class to compose a BQM model from the abstract multiplication table (described by class multiplication_table) of two abstract binary numbers (descibed by class abstract_bin_num)
class BQM_from_multiplication_table( multiplication_table, reduce_higher_order_polynomials ):


	##
	# @brief Constructor of the class. Values num1 and num2 are stores by class attributes _p and _q such that bit_length(_p) >= bit_length(_q)
	# @param num1 The first abstract binary number (an instance of class abstract_bin_num)
	# @param num2 The second abstract binary number (an instance of class abstract_bin_num)
	def __init__( self, num1, num2, target_num ):
		multiplication_table.__init__(self, num1, num2)
		reduce_higher_order_polynomials.__init__(self)

		# test the types of the input parameters
		if not isinstance(target_num, bin_num):
			raise Exception('target_num is not valid input type')

		# The number to be factorized given as an instance of class abstract_binary.binary_number.bin_num
		self._target_num = target_num

		# The dictionary of the BQM cost function
		self._cost_function = dict()

		# The constant termn in the cost function
		self._cost_function_constant = 0


	##
	# @brief Adds penalties to the cost function stored in the class
	def add_penalties_to_cost_function( self ):
		for penalty in self._penalties.values():
			for item in penalty.items():
				if item[0] in self._cost_function.keys():
					self._cost_function[item[0]] = self._cost_function[item[0]] + item[1]
				else:
					self._cost_function[item[0]] = item[1]
		if DEBUG:
			print(' ')
			print('The generated cost function including the penalties:')
			print( self._cost_function )
			print('The constant part of the cost function is:' + str(self._cost_function_constant) )


	##
	# @brief Ads BQM term to the cost function.
	# @param BQM_to_add A dictionary containing the BQM terms.
	# @param constant_2_add A constant to be added to the coantant part of the cost function
	def add_to_cost_function(self, BQM_to_add, constant_2_add=0):

		for key in BQM_to_add.keys():
			if key in self._cost_function.keys():
				self._cost_function[key] = self._cost_function[key] + BQM_to_add[key]
			else:
				self._cost_function[key] = BQM_to_add[key]

		self._cost_function_constant = self._cost_function_constant + constant_2_add

	##
	# @brief Gets the calculated cost function and its contant part in form of a (dict, constants) tuple.
	# @return Returns with the cost function and its contant part in form of a (dict, constants) tuple.
	def get_cost_function(self):
		return (self._cost_function, self._cost_function_constant)

	##
	# @brief Generate the cost function (pq-n)**2 for the bits of a given block for qbsolv. The higher order terms are reduced to quadratic forms
	# @param block_id >= 0 The number identificating the corresponding block
	# @param update_cost_function Logical variable. Set true to update the stored cost function with the new block, ot set to False to owerride the stored cost function
	def cost_function_of_block( self, block_id, update_cost_function = False ):
		self._substituted_vars.keys()
		#The dictionary describing the binary polinomial of the cost function
		cost_function = dict()

		# obtain the pq-n BQM model of a given block
		block_BQM_dict = self.sum_up_block( block_id )

		# generate (pq-n)^2 from the dictionary of pq-n
		keys = list( block_BQM_dict.keys() )
		constant = 0
		for key_id_1 in range(0, len(keys)):
			key_1 = keys[key_id_1]
			value_1 = block_BQM_dict[key_1]

			# first setting the diagonal terms of the product pq, using x_i**2 = x_i for binary variables
			if key_1 == CONST:
				constant = constant + value_1**2
			else:
				if isinstance( key_1, str ):
					key_new = (key_1,key_1)
				elif isinstance( key_1, tuple ):
					key_new = key_1
				else:
					raise('Bad key value: ' + str(key_1))
	
				if key_new in cost_function.keys():
					cost_function[ key_new ] = cost_function[ key_new ] + value_1**2  # For qbsolv (dimod) the linear terms must (might) be represented by tuples
				else:
					cost_function[ key_new ] = value_1**2  # For qbsolv (dimod) the linear terms must (might) be represented by tuples


			# now creating the offdiaginal terms of the product pq,
			# using x_i**2 = x_i for binary variables, and the reduction of the higher ored terms by class reduce_higher_order_polynomials
			for key_id_2 in range(key_id_1+1, len(keys)):
				key_2 = keys[key_id_2]
				value_2 = block_BQM_dict[key_2]
				value_new = 2*value_1*value_2

				if key_1 == CONST:
					# For qbsolv (dimod) the linear terms must (might) be represented by tuples
					if isinstance( key_2, str ):
						key_new = (key_2,key_2)
					elif isinstance( key_2, tuple ):
						key_new = key_2
					else:
						raise('Bad key value: ' + str(key_2))
				elif key_2 == CONST:
					# For qbsolv (dimod) the linear terms must (might) be represented by tuples
					if isinstance( key_1, str ):
						key_new = (key_1,key_1)
					elif isinstance( key_1, tuple ):
						key_new = key_1
					else:
						raise('Bad key value: ' + str(key_2))
				elif isinstance(key_1, str) and isinstance(key_2, str):
					key_new = [ key_1, key_2 ]
					key_new.sort()
					key_new = tuple(key_new)
				elif isinstance(key_1, tuple) and isinstance(key_2, str):
					if key_2 in key_1:
						key_new = key_1
					else:
						# introduce a new variable (or retrive an existing one) for the substitution
						subs_var = self.set_substitution( key_1 )
						# set the new key for the BQM dictionary
						key_new = [ subs_var, key_2 ]
						key_new.sort()
						key_new = tuple(key_new)
						# creating (or increasing) the panelty for the substitution
						self.set_penalty( subs_var, self._penalty_amplitude )
					
				elif isinstance(key_1, str) and isinstance(key_2, tuple):
					if key_1 in key_2:
						key_new = key_2
					else:
						key_new = ( key_1, self.set_substitution( key_2 ) )	
						# introduce a new variable (or retrive an existing one) for the substitution
						subs_var = self.set_substitution( key_2 )
						# set the new key for the BQM dictionary
						key_new = [ key_1, subs_var ]
						key_new.sort()
						key_new = tuple(key_new)
						# creating (or increasing) the panelty for the substitution
						self.set_penalty( subs_var, self._penalty_amplitude )		
		
				elif isinstance(key_1, tuple) and isinstance(key_2, tuple):
					if key_1 == key_2:
						key_new = key_1
					else:
						key_new = ( self.set_substitution( key_1 ), self.set_substitution( key_2 ) )
						# introduce a new variables (or retrive an existing one) for the substitution
						subs_var_1 = self.set_substitution( key_1 )
						subs_var_2 = self.set_substitution( key_2 )
						# set the new key for the BQM dictionary
						key_new = [ subs_var_1, subs_var_2 ]
						key_new.sort()
						key_new = tuple(key_new)
						# creating (or increasing) the panelty for the substitution
						self.set_penalty( subs_var_1, self._penalty_amplitude )
						self.set_penalty( subs_var_2, self._penalty_amplitude )
				else:
					continue

					
				if key_new in cost_function.keys():
					cost_function[ key_new ] = cost_function[ key_new ] + value_new
				else:
					cost_function[ key_new ] = value_new



		#print( len(cost_function.keys()) )
		#print( len(keys) )

		if DEBUG:
			print(' ')
			print('The generated cost function of the block ' + str(block_id) )
			print( cost_function )
			print('The constant part of the cost function is:')
			print(constant)
			print('The variable substitutions are:')
			print( self.get_substitutions() )
			print('The created penalties:')
			print( self.get_penalties() )


		if update_cost_function:
			# updating the cost function stored by the class
			self.add_to_cost_function( cost_function, constant )
		else:
			# replacing the cost function stored by the class
			self._cost_function = cost_function 
			self._cost_function_constant = constant

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

			# Now add the carry in the given column from the BQM model
			carry = self.get_carry(col)
			if type(carry) == str:
				block_BQM_dict[ carry ] = 2**power
			elif carry != None:
				block_BQM_dict[ CONST ] = block_BQM_dict[ CONST ] + carry*2**power
			else:
				pass
			

			# Now add the bits of the target number to the block BQM model
			target_bit = self._target_num.get_bit(col)
			if DEBUG:
				print('The target bit of col=' + str(col) + ' :' + str(target_bit)) 
			block_BQM_dict[ CONST ] = block_BQM_dict[ CONST ] - target_bit*2**power

			# increase the power for the next column
			power = power + 1


		# subtrack the carry bits from the next column block
		if block_id < block_num-1 and block_id > 0:

			# determine the columns in the next block
			cols = list()
			for col_tmp in range( self._block_list[block_id]+1, self._block_list[block_id+1]+1 ):
				cols.append(col_tmp)

			if DEBUG:
				print('\nThe columns involved in the next block (to acount for the carries): ' + str(cols))

			for col in cols:
			# Now subtrack the carry in the given column from the BQM model
				carry = self.get_carry(col)
				if type(carry) == str:
					block_BQM_dict[ carry ] = -2**power
				elif carry != None:
					block_BQM_dict[ CONST ] = block_BQM_dict[ CONST ] - carry*2**power
				else:
					pass

				# increase the power for the next column
				power = power + 1
			

		if DEBUG:
			print('\nThe BQM model of the block=' + str(block_id) + ' :' + str(block_BQM_dict)) 

		return block_BQM_dict


