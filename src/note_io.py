import io
import os

#TODO Replace each print function to a suitable error for UI
def read_note(vault_path,note_path) -> str:
    "given a path read the note(md) file"
    path = os.path.join(vault_path,note_path)
    if os.path.exists(path) and os.path.isfile(path):
        if path.endswith(".md"):
            try:
                with open(path, encoding="utf-8") as f:
                    read_data = f.read()
                    return read_data
            except:
                print(f"Error: reading from file: {path}")

        else:
            print("Error: invalid file format to read")
            return None
    else:
        print("Error: invalid file path to read")
        return None


def write_note(vault_path,note_path,note: str) -> None:
    "writes raw md string to the given path file"
    path = os.path.join(vault_path,note_path)
    if os.path.exists(os.path.dirname(path)):
        if path.endswith(".md"):
            try:
                with open(path, encoding="utf-8") as f:
                    f.write(note)
                    
            except:
                print(f"Error: writing to file: {path}")
        else:
            print("Error: invalid file format to write")
            return
    else:
        print("Error: invalid parent folder path to Write")
        return
    pass

def read_vault_folder(vault_root: str) -> list:
    "scans a folder for notes and returns a list of notes relative paths"

    path_list = []
    for root , _ , files in os.walk(vault_root):
        for file in files:
            if file.endswith(".md"):
                abs_path = os.path.join(root,file)
                relative_path = os.path.relpath(abs_path,vault_root)
                path_list.append(relative_path)
    return path_list

