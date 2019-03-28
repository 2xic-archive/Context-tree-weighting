import numpy as np

class tree_objects:
	def __init__(self, A, B, P_E, P_W):
		self.A = A
		self.B = B
		self.P_W = P_W
		self.P_E = P_E
	
	def __str__(self):
		return "P_E ={}	P_W={} A={}	B={}".format(self.P_E, self.P_W, self.A, self.B)

class tree_nodes:
	def __init__(self, symbol_range=256):
		self.height = 0
		self.symbol_range = symbol_range
		self.leafs = [None] * symbol_range

		self.A = 0
		self.B = 0
		self.P_E = 0
		self.P_W = 0

	def __str__(self):
		return "P_E ={}	P_W={} A={}	B={}".format(self.P_E, self.P_W, self.A, self.B)

	def proability_estimator_zero(self):
		P_E = self.P_E + np.log((self.A + 0.5) / 
								(self.A + self.B + 1))
		A = self.A + 1
		B = self.B
		return P_E, A, B
	
	def probability_estimator_one(self):
		P_E = self.P_E + np.log((self.B + 0.5) / 
								(self.A + self.B + 1))
		A = self.A
		B = self.B + 1 
		return P_E, A, B

	def contains_leaf(self):
		contains_leaf = False
		for leaf in self.leafs:
			if not (leaf == None):
				contains_leaf = True
				break
		return contains_leaf

	def get_leaf_value(self, symbol):
		if(self.leafs[symbol] == None):
			return 0
		else:
			return self.leafs[symbol].P_W

	def adjust_node(self, bit, previous_bit, leaf, update_nodes=True):
		A = 0 
		B = 0
		P_E = 0
		P_W = 0

		if(bit == 0):
			P_E, A, B = self.proability_estimator_zero()
		else:
			P_E, A, B = self.probability_estimator_one()

		if(self.contains_leaf()):
			leafs_value_weight = 0
			for symbol in range(self.symbol_range):
				if(symbol == previous_bit):
					leafs_value_weight += leaf.P_W
				else:
					leafs_value_weight += self.get_leaf_value(symbol)
			P_W = np.logaddexp(np.log(0.5) + P_E,
								np.log(0.5) + leafs_value_weight )	
		else:
			P_W =  P_E

		if update_nodes:
			self.P_E = P_E
			self.P_W = P_W
			self.A = A
			self.B = B

		return tree_objects(A, B, P_E, P_W)

	def get_leaf(self, symbol):
		if(symbol < len(self.leafs)):
			if(self.leafs[symbol] == None):
				self.leafs[symbol] = tree_nodes(self.symbol_range)
				self.leafs[symbol].height = self.height + 1
			return self.leafs[symbol]
		else:
			raise Exception("Bad symbol or symbol_range")

class tree:
	def __init__(self, symbol_range=256):
		self.symbol_range = symbol_range
		self.trees = {

		}

	def get_tree(self, byte):
		if(byte not in self.trees):
			self.trees[byte] = tree_nodes(self.symbol_range)
		return self.trees[byte]

	def update_tree(self, tree_node, context, bit, update_nodes):
		previous_bit = None
		leaf = None
		if context:
			previous_bit = context.pop()
			leaf = self.update_tree(tree_node.get_leaf(previous_bit), context, bit, update_nodes)
		return tree_node.adjust_node(bit, previous_bit, leaf, update_nodes)

	def travel_tree_update_value(self, context, byte, bit):
		return self.update_tree(self.get_tree(byte), context[:], bit, update_nodes=True)	

	def travel_tree_get_value(self, context, byte, bit):
		return self.update_tree(self.get_tree(byte), context[:], bit, update_nodes=False)	

	def find_probability(self, context, byte):
		zero = self.travel_tree_get_value(context, byte, 0)
		one = self.travel_tree_get_value(context, byte, 1)
		return np.exp(zero.P_W - np.logaddexp(zero.P_W, one.P_W))


