# Vault class and related helper functions for IO and stats


class Vault():
    def __init__(self,root_folder):
        self.path = root_folder
        self.notes_headers = {}
        self.note_tree = {}
        self.graph = None
    #get all notes in the root folder and update self.notes and self.note_tree
    
def refresh(vault):
    "refreshes vault class with any new modifications in the vault"
    pass

def parse_vault_folder(vault):
    "parses the vault folder to update vault.note_tree"
    pass

def read_all_note_headers(vault):
    "reads every note in the note_tree to update vault.notes_headers"
    pass
def read_note(path):
    "given a path read the note(md) file"
    pass
def write_note(note,path):
    "writes raw md string to the given path file"
    pass


