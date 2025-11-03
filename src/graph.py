#creating graph objects and managing them

import networkx as nx

def create_graph(vault):
    pass

def get_most_connected(graph, n = 10):
    "Gets top n most connected nodes in the graph"
    pass

def get_orphaned_notes(graph):
    "Return notes with no incoming or outgoing links."
    pass

def get_backlinks(graph, note_title):
    "Get all notes that link TO this note."
    pass

def get_outgoing_links(graph, note_title):
    "Get all notes this note links to."
    pass

