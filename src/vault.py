# Vault class and related helper functions for IO and stats

from note_io import *
from note import Note

#TODO: refresh is called reactively so when there is a read or write

class Vault():
    def __init__(self,root_folder):
        self.root_path = root_folder
        self.notes = {} # note relative paths keys and note objects as values
        self.note_relative_paths = []
        self.graph = None

        self.refresh() #inits vault by refreshing


    
    def refresh(self) -> None:
        "refreshes vault class with any new modifications in the vault"
        self.note_relative_paths = read_vault_folder(self.root_path)
        self.load_all_notes()
    
    def refresh_single(self,path) -> None:
        self.load_note(path)
        #TODO refresh the graph too

    def load_all_notes(self) -> None:
        "reads every note in the note_tree to update self.notes_headers"
        for path in self.note_relative_paths:
            self.load_note(path)

    def load_note(self,path) -> None:
        md = read_note(self.root_path,path)
        note = Note(md)
        self.notes[path] = note
