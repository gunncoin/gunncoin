"""

A list of the all trusted nodes ip's

Note: This has to be hard coded in order to first connect to the network 
(or we can just ping every possible combination of an ip, but like...)

127.0.0.1 is for local testing purposes

"""

from random import choice

trusted_nodes = ["127.0.0.1"]

def get_random_explorer_node():
    choice(trusted_nodes)