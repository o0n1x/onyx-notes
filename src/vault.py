# Vault class and related helper functions for IO and stats


class Vault():
    def __init__(self,root_folder):
        self.path = root_folder
        self.notes_headers = {}
        self.note_tree = {}
        self.graph = None

    

    def refresh(self):
        "refreshes vault class with any new modifications in the vault"
        pass


    def read_all_note_headers(self):
        "reads every note in the note_tree to update self.notes_headers"
        pass


