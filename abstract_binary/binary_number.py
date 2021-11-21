from .base import *

			
		

##
# @brief class representing a binary number
class bin_num():

	##
	# @brief Constructor of the class.
	# @param represented_num The number to be represented by the class
	# @param type The type of the variable stored_num: 'decimal' (optional), or 'binary'
	def __init__( self, represented_num, FORMAT=num_format.DEC ):
		
		# The represented number in binary format
		if FORMAT==num_format.DEC:
			self._represented_num = bin(represented_num)
		elif  FORMAT==num_format.BIN:
			self._represented_num = represented_num
			
		#print( self._represented_num )
		
	
	##
	# @brief Get the number of binary digits of the represented number
	# @return Returns the number of the binary digits
	def bit_length( self ):
		# the first two chars (0b) are not counted
		return len( self._represented_num ) - 2

	##
	# @brief Get the bit xi 
	# @param i The bit index to be queried (i>=0)
	# @return Returns the number of the binary digits
	def get_bit( self, i ):
		# Test whether i is valid
		if 0<=i and i<self.bit_length():
			return int(self._represented_num[-i-1])
		elif i>=self.bit_length():
			return 0
		else:
			raise('Bit index i is not valid')
		
		
	##
	# @brief Increase the number of bits in the representation of the number. (In practice zeros are adde to the front of the binary representation)
	# @param num_of_digits The number of the bits in the binary representation is increased by num_of_digits.
	def increase_bit_length( self, num_of_digits ):
		self._represented_num = self._represented_num[0:2] + num_of_digits*"0" + self._represented_num[2:]
		print( self._represented_num )
		print( self._represented_num[0:2] )
		
