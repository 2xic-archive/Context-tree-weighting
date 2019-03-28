from arithmetic_coding import *
from weighted_tree import *

class ctw:
	def __init__(self, data, tree_depth):
		self.tree_depth = tree_depth
		self.data = data

		self.tree = tree()
		self.context = [0] * self.tree_depth

	def slide_context_window(self, value):
		if(type(value) == str):
			value = ord(value)
		self.context = self.context[1:] + [value]

	def parse_input(self, byte, index):
		if(type(byte) == int):
			return (byte >> (7 - index)) & 1
		else:
			return (ord(byte) >> (7 - index)) & 1
	
class ctw_encoder(ctw):
	def __init__(self, data, tree_depth):
		super().__init__(data, tree_depth)
		self.encoder = encoder()

	def encode(self):
		for byte in self.data:
			byte_in_parts = ()
			for bit_index in range(8):
				bit = self.parse_input(byte, bit_index)
				self.encoder.encode(self.tree.find_probability(self.context, byte_in_parts), bit)
				self.tree.travel_tree_update_value(self.context, byte_in_parts, bit)
				byte_in_parts += (bit, )
			self.slide_context_window(byte)
		return self.encoder.get_output()

class ctw_decoder(ctw):
	def __init__(self, data, data_length, tree_depth):
		super().__init__(data, tree_depth)
		self.decoder = decoder(data)
		self.data_length = data_length

	def reconstruct_byte(self, byte_in_parts):
		byte_reconstructed = 0
		for bit in byte_in_parts:
			byte_reconstructed = (byte_reconstructed << 1) | bit
		return byte_reconstructed

	def decode(self):
		for byte_index in range(self.data_length // 8):
			byte_in_parts = ()
			for bit_index in range(8):
				bit = self.decoder.decode(self.tree.find_probability(self.context, byte_in_parts))
				self.tree.travel_tree_update_value(self.context, byte_in_parts, bit)
				byte_in_parts += (bit, )			
			self.slide_context_window(self.reconstruct_byte(byte_in_parts))
		return self.decoder.get_output()

if __name__ == "__main__":
	tree_depth = 4
	input_text = open("input.txt", "r").read()
	encoder = ctw_encoder(input_text, tree_depth)
	length, encoded_data = encoder.encode()
	
	open("encoded", "wb").write(encoded_data)

	decoder = ctw_decoder(encoded_data, length, tree_depth)
	length, decoded_data = decoder.decode()

	open("decoded", "w").write("".join(map(chr, decoded_data)))

	if(type(input_text) == str):
		assert "".join(map(chr, decoded_data)) == input_text
	else:
		assert "".join(map(chr, decoded_data)) == "".join(map(chr, input_text))


