import sys
from pathlib import Path

# Add the parent directory (src) to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import os
from vault import Vault
from note import Note
from generate_vaults import main as generate

#test vaults' paths
ROOT = "src/unittests/test_vaults/"

EMPTY_VAULT_PATH = ROOT + "empty_vault"
SINGLE_NOTE_VAULT_PATH = ROOT + "single_note_vault"
MULTIPLE_NOTES_VAULT_PATH = ROOT + "multiple_note_vault"
NESTED_NOTES_VAULT_PATH = ROOT + "nested_notes_vault"
NONMD_MD_VAULT_PATH = ROOT + "nonmd_md_vault"
NONMD_ONLY_VAULT_PATH = ROOT + "nonmd_only_vault"

md =  """---
title: My First Note
tags: [example, demo]
created: 2025-11-01 17:35:50
modified: 2025-11-02 14:30:00
---

# My First Note

This is a simple example note with frontmatter metadata.

## What is Frontmatter?

Frontmatter is the YAML metadata at the top of the file, enclosed between `---` markers. It contains structured data about the note.

## Links to Other Notes

You can link to other notes using double brackets: [[Python Basics]] or [[Django Tutorial]].

## Content

Write your notes here in regular markdown:

- Bullet points work
- **Bold text** works
- *Italic text* works
- `code snippets` work

```python
# Code blocks work too
def hello():
    print("Hello, world!")
```"""

md_edited =  """---
title: My First Note
tags: [example, edited]
created: 2025-11-01 17:35:50
modified: 2025-11-02 14:30:00
---

# My First Note

This is a simple example note with frontmatter metadata.

"""

class TestVault(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = generate()

    def test_single_note_vault(self):
        #tests a simple case to check if init is working


        vault = Vault(SINGLE_NOTE_VAULT_PATH)
        self.assertListEqual(vault.note_relative_paths,["example.md"])
        self.assertDictEqual(vault.notes,{"example.md":Note(md)})
    
    def test_multiple_notes_vault(self):
        vault = Vault(MULTIPLE_NOTES_VAULT_PATH)
        self.assertEqual(len(vault.note_relative_paths),10)

    def test_vault_loads_nested_folders(self):
        vault = Vault(NESTED_NOTES_VAULT_PATH)
        self.assertEqual(len(vault.note_relative_paths),28)
    
    def test_vault_ignores_non_md_files(self):
        vault = Vault(NONMD_MD_VAULT_PATH)
        self.assertEqual(len(vault.note_relative_paths),7)

    def test_empty_vault(self):
        vault = Vault(EMPTY_VAULT_PATH)
        self.assertEqual(len(vault.note_relative_paths),0)
        
    def test_empty_vault_with_files(self):
        vault = Vault(NONMD_ONLY_VAULT_PATH)
        self.assertEqual(len(vault.note_relative_paths),0)

    def test_vault_refresh_picks_up_new_notes(self):
        vault = Vault(ROOT + "test_vault")
        self.assertEqual(len(vault.note_relative_paths),0)
        with open(ROOT + "test_vault" + '/example.md','w') as f:
            f.write(md)
        vault.refresh()
        self.assertEqual(len(vault.note_relative_paths),1)
        
    
    def test_vault_refresh_removes_deleted_notes(self):
        vault = Vault(ROOT + "test_vault2")
        self.assertEqual(len(vault.note_relative_paths),1)
        os.remove(ROOT + "test_vault2" + '/example.md')
        vault.refresh()
        self.assertEqual(len(vault.note_relative_paths),0)

    def test_vault_refresh_single_updates_one_note(self):
        vault = Vault(ROOT + "test_vault3")
        self.assertEqual(len(vault.note_relative_paths),2)
        note = vault.notes["python_basics.md"]
        tags = note.tags
        self.assertEqual(vault.notes["python_basics.md"].tags,["example","demo"])

        with open(ROOT + "test_vault3" + "/python_basics.md","w") as f:
            f.write(md_edited)
        vault.refresh()
        self.assertNotEqual(tags,vault.notes["python_basics.md"].tags)
        with open(ROOT + "test_vault3" + "/python_basics.md","w") as f:
            f.write(md)
    

    def test_vault_refresh_updates_modified_notes(self):
        vault = Vault(ROOT + "test_vault3")
        self.assertEqual(len(vault.note_relative_paths),2)
        note = vault.notes["python_basics.md"]
        tags = note.tags #both notes use the same tags so we wont duplicate
        self.assertEqual(vault.notes["python_basics.md"].tags,["example","demo"])
        self.assertEqual(vault.notes["database_design.md"].tags,["example","demo"])

        with open(ROOT + "test_vault3" + "/python_basics.md","w") as f:
            f.write(md_edited)
        with open(ROOT + "test_vault3" + "/database_design.md","w") as f:
            f.write(md_edited)
        vault.refresh()
        self.assertNotEqual(tags,vault.notes["python_basics.md"].tags)
        self.assertNotEqual(tags,vault.notes["database_design.md"].tags)
        with open(ROOT + "test_vault3" + "/python_basics.md","w") as f:
            f.write(md)
    

#integration test

    def test_vault_handles_notes_without_frontmatter(self):
        vault = Vault(ROOT + "without_frontmatter_vault")
        self.assertEqual(len(vault.note_relative_paths),1)
        self.assertEqual(vault.notes["no_frontmatter.md"].tags , [])
        self.assertEqual(vault.notes["no_frontmatter.md"].title , "Untitled Note")
        #for manual checking
        with open(ROOT + "without_frontmatter_vault" + "/no_frontmatter.md","w") as f:
            f.write(vault.notes["no_frontmatter.md"].get_formatted_md())
        vault.refresh()
        self.assertEqual(vault.notes["no_frontmatter.md"].tags , [])
        self.assertEqual(vault.notes["no_frontmatter.md"].title , "Untitled Note")
    





if __name__ == "__main__":
    unittest.main()