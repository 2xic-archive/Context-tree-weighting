class shared:
	def __init__(self, encoding):
		self.byte = 0
		self.bit_index = 0
		self.byte_index = 0

		self.decode_bit = 0
		self.decode_byte_index = 0

		self.output = []
		self.length = 0

		self.interval_a = 0
		self.interval_b = 0xFF

		self.encoding = encoding
		self.written_output = False

	def finished_byte(self):
		self.bit_index += 1
		if(self.bit_index == 8):
			self.byte_index += 1
			self.bit_index = 0
			return True
		return False		

	def write_out_byte(self, bit):
		self.byte = (self.byte << 1) | bit
		
		if(self.finished_byte()):
			self.output.append(self.byte)
			self.byte = 0

	def move_interval(self):
		self.interval_a = (self.interval_a << 1) & 0xFF
		self.interval_b = ((self.interval_b << 1) & 0xFF) | 0x01

	def split_interval(self, probability, bit):
		interval_range = self.interval_b - self.interval_a + 1
		scaled_range = int(probability * interval_range)

		if(scaled_range == 0):
			scaled_range = 1
		elif(scaled_range == interval_range):
			scaled_range = interval_range - 1

		if not self.encoding:
			#	reverse encoding, check lines below!
			zero_range = self.interval_a + scaled_range - 1
			if(bit <= zero_range):
				self.write_out_byte(0)
				bit = 0
			else:
				self.write_out_byte(1)
				bit = 1

		if(bit == 0):
			self.interval_b = self.interval_a + scaled_range - 1
		elif(bit == 1):
			self.interval_a = self.interval_a + scaled_range
		else:
			raise Exception("Not a bit.")
		return bit

	def move_byte_window(self):
		self.decode_bit += 1
		if(self.decode_bit == 8):
			self.decode_byte_index += 1
			self.decode_bit = 0

	def padding_interval(self):
		assert self.encoding != None
		while (self.interval_a >> 7) == (self.interval_b >> 7):
			if(self.encoding):
				self.write_out_byte(self.interval_a >> 7)	#	MSP won't change
			else:
				self.move_byte_window()
			self.move_interval()

	def clear_byte(self):
		for bit_index in range(7, -1, -1):
			self.write_out_byte(int(bool((self.interval_a & (1 << bit_index)))))

	def clear_byte_from_index(self):
		while self.bit_index > 0:
			self.write_out_byte(0)

	def get_output(self):
		if not self.written_output:
			if(self.encoding):
				self.clear_byte()
				self.write_out_byte(0)	
			self.clear_byte_from_index()
			self.written_output = True	
		return self.length, bytearray(self.output)


class encoder(shared):
	def __init__(self):
		super().__init__(encoding = True)

	def encode(self, probability, bit):
		self.padding_interval()
		self.split_interval(probability, bit)
		self.length += 1

class decoder(shared):
	def __init__(self, encoded_input):
		super().__init__(encoding=False)
		self.encoded_input = list(encoded_input)

	def stream_bits(self):
		#	want to have a moving window of bits, "streamed"
		MSB = (self.encoded_input[self.decode_byte_index])
		LSB = (self.encoded_input[self.decode_byte_index + 1])

		#	don't want to overflow...
		MSB = (MSB << self.decode_bit) & 0xFF 
		LSB = LSB >> (8 - self.decode_bit)

		return (MSB | LSB)

	def decode(self, probability):
		self.padding_interval()
		return self.split_interval(probability, self.stream_bits())

