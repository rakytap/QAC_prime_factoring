from .base import *

##
# @brief Protoype class of a binary (unknown) number of a format "number = sum( 2^i*x_i )", i in (0,n-1), where n is the bit length of the represented number, and x_i are the unknown (or partially unknown) bits.
class abstract_bin_num():

	##
	# @brief Constructor of the class.
	# @param num_length The number of bits representing the number
	def __init__( self, num_bits ):
		## The number of bits of the represented number
		self._num_bits = num_bits
		## The dictionary of the known bits "i": True or False
		self._known_bits = dict()
		## dictionary used to label the bits
		self._bit_labels = dict()
		
	##
	# @brief Add a known bit to the number representation
	# @param i The index labeling the bit
	# @param xi The bit to be added to the abstract number (1 or 0)
	def set_bit( self, i, xi ):
		if i >= self._num_bits:
			raise Exception('i should be smaller than the number of represented bits')

		# chekck the input value
		if xi in BIT_VALUES:			
			self._known_bits[str(i)] = xi
		else:
			raise Exception('The possible values of xi must be in ' + BIT_VALUES)

	##
	# @brief Get the dictionary of the bit labels
	# @return Returns with the dictionary of (i: bit_label)
	def get_bit_labels( self ):
		return self._bit_labels



	##
	# @brief Set a label for a specific bit
	# @param i The ordinal number of the bit x_i
	# @param bit_label The label of bit x_i
	def set_bit_label( self, i, bit_label ):
		self._bit_labels[i] = bit_label

	##
	# @brief Check whether a given bit x_i is defined or not
	# @param i The ordinal number of the bit x_i
	# @return Returns with True if the bit x_i is defined, False otherwise
	def check_bit( self, i ):
		if i >= self._num_bits:
			raise Exception('i should be smaller than the number of represented bits')
		
		return str(i) in self._known_bits.keys()	


	##
	# @brief Gets the x_i bit of the represented number
	# @param i The ordinal number of the bit x_i
	# @return Returns with the value of bit x_i
	def get_bit( self, i ):
		if i >= self._num_bits:
			raise Exception('i should be smaller than the number of represented bits')

		return self._known_bits[str(i)]


		
	##
	# @brief Increase the number of bits in the representation of the number. (In practice zeros are adde to the front of the binary representation)
	# @param num_of_digits The number of the bits in the binary representation is increased by num_of_digits.
	def increase_bit_length( self ):
		self._num_bits = self._num_bits + 1	
		
		
	##
	# @brief Determines the binary form of the represented abstract number (x_n-1, ... x_1,x_0)
	# @return Returns with a string of the binary form of the represented number. If there are still undetermined bits, the function returns with None
	def binary_form( self ):
		# checking if there are still undetermined bits
		if len( self._known_bits ) < self._num_bits:
			print( 'There are still undefined bits in the represented number' )
			return			
		
		binary_form = ''			
		for i in range(0, self._num_bits):
			binary_form = binary_form + str(self._known_bits[ str(i) ])
			
		binary_form = '0b' + binary_form	
		return(binary_form)
		

	##
	# @brief Get the decimal representation of the number if all the bits are defined
	# @return Returns with the decimal representation of the number, or with None if not all the bit are defined
	def get_decimal( self ):
		dec_value = 0

		# check whether all bits are deined or not
		for bit in range(0, self.bit_length()):
			if str(bit) in self._known_bits.keys():
				dec_value = dec_value + self._known_bits[str(bit)]*(2**bit)
			else:
				return None

		return dec_value
		
			
		
	##
	# @brief Get the number of binary digits of the represented number
	# @return Returns the number of the binary digits
	def bit_length( self ):
		return self._num_bits
		
			
