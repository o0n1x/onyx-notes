# Vault class and related helper functions for IO and stats

#TODO: refresh is called reactively so when there is a read or write

class Vault():
    def __init__(self,root_folder):
        self.root_path = root_folder
        self.notes_headers = {} # note relative paths keys and headers as values
        self.note_relative_paths = []
        self.graph = None

    

    def refresh(self) -> None:
        "refreshes vault class with any new modifications in the vault"
        pass


    def read_all_note_headers(self) -> None:
        "reads every note in the note_tree to update self.notes_headers"
        pass


