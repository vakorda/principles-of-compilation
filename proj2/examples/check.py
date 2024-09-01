import pickle
from lark import Lark

p2file = open("proj2/examples/onetoten_pt_node.pkl", "rb")
write17_tree2 = pickle.load(p2file)

write17_tree2.dump()