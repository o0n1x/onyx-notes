"""
code generated with Claude to generate vaults for testing

"""



import os
import random
from datetime import datetime, timedelta

def generate_frontmatter(title, tags=None, created=None):
    """Generate YAML frontmatter for a note."""
    if tags is None:
        tags = random.sample(['python', 'testing', 'notes', 'example', 'demo', 'tutorial'], k=random.randint(1, 3))
    
    if created is None:
        days_ago = random.randint(0, 30)
        created = datetime.now() - timedelta(days=days_ago)
    
    modified = created + timedelta(hours=random.randint(1, 72))
    
    frontmatter = f"""---
title: {title}
tags: {tags}
created: {created.strftime('%Y-%m-%d %H:%M:%S')}
modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}
---
"""
    return frontmatter

def generate_lorem_paragraphs(num_paragraphs=3):
    """Generate lorem ipsum paragraphs."""
    lorem_sentences = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum.",
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia.",
        "Nisi ut aliquip ex ea commodo consequat.",
        "Deserunt mollit anim id est laborum.",
        "Sed ut perspiciatis unde omnis iste natus error sit voluptatem.",
        "Accusantium doloremque laudantium, totam rem aperiam.",
        "Eaque ipsa quae ab illo inventore veritatis et quasi architecto."
    ]
    
    paragraphs = []
    for _ in range(num_paragraphs):
        num_sentences = random.randint(3, 6)
        paragraph = " ".join(random.sample(lorem_sentences, num_sentences))
        paragraphs.append(paragraph)
    
    return "\n\n".join(paragraphs)

def generate_note(title, num_paragraphs=3, add_links=True):
    """Generate a complete markdown note."""
    content = f"# {title}\n\n"
    content += generate_lorem_paragraphs(num_paragraphs)
    
    if add_links:
        link_options = ["Related Note", "See Also", "Previous", "Next Topic", "Reference"]
        num_links = random.randint(1, 3)
        content += "\n\n## Related Notes\n\n"
        for _ in range(num_links):
            link_title = random.choice(link_options) + " " + str(random.randint(1, 100))
            content += f"- [[{link_title}]]\n"
    
    frontmatter = generate_frontmatter(title)
    return frontmatter + "\n" + content

def create_vault_structure(vault_path, structure):
    """Create a vault with specified structure."""
    os.makedirs(vault_path, exist_ok=True)
    
    for name, value in structure.items():
        path = os.path.join(vault_path, name)
        
        if isinstance(value, dict):
            # It's a folder
            create_vault_structure(path, value)
        else:
            # It's a note
            title = name.replace('.md', '').replace('_', ' ').title()
            note_content = generate_note(title)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(note_content)

def main():
    base_path = 'src/unittests/test_vaults'
    
    # empty_vault - just create the folder
    os.makedirs(f'{base_path}/empty_vault', exist_ok=True)

    #used for testing refresh function
    os.makedirs(f'{base_path}/test_vault', exist_ok=True) #new notes
    if os.path.exists(base_path + "/test_vault" + '/example.md'):
        os.remove(base_path + "/test_vault" + '/example.md')
    os.makedirs(f'{base_path}/test_vault2', exist_ok=True) # delete notes

    os.makedirs(f'{base_path}/test_vault3', exist_ok=True) #modify notes

    os.makedirs(f'{base_path}/without_frontmatter_vault', exist_ok=True) #integration test

    data = """---
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

    data_no_frontmatter = """

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

    with open(f'{base_path}/test_vault2/example.md','w') as f:
        f.write(data)
    
    with open(base_path + "/test_vault3" + "/python_basics.md","w") as f:
            f.write(data)
    with open(base_path + "/test_vault3" + "/database_design.md","w") as f:
            f.write(data)

    with open(base_path + "/without_frontmatter_vault" + "/no_frontmatter.md","w") as f:
            f.write(data_no_frontmatter)

    os.makedirs(f'{base_path}/single_note_vault', exist_ok=True)
    with open(f'{base_path}/single_note_vault/example.md','w') as f:
        f.write(data)
   
    
    # multiple_note_vault - 10 notes in root folder
    multi_vault = {
        'getting_started.md': True,
        'python_basics.md': True,
        'data_structures.md': True,
        'algorithms.md': True,
        'web_development.md': True,
        'database_design.md': True,
        'api_tutorial.md': True,
        'testing_guide.md': True,
        'deployment_notes.md': True,
        'best_practices.md': True
    }
    create_vault_structure(f'{base_path}/multiple_note_vault', multi_vault)
    
    # nested_notes_vault - deep folder structure with many notes
    nested_vault = {
        'index.md': True,
        'quick_reference.md': True,
        'Programming': {
            'python.md': True,
            'javascript.md': True,
            'rust.md': True,
            'Frameworks': {
                'django.md': True,
                'flask.md': True,
                'react.md': True,
                'Advanced': {
                    'performance_optimization.md': True,
                    'design_patterns.md': True
                }
            },
            'Tools': {
                'git.md': True,
                'docker.md': True,
                'vim.md': True
            }
        },
        'Mathematics': {
            'linear_algebra.md': True,
            'calculus.md': True,
            'statistics.md': True,
            'Advanced': {
                'category_theory.md': True,
                'topology.md': True
            }
        },
        'Projects': {
            'project_ideas.md': True,
            'Active': {
                'note_app.md': True,
                'web_scraper.md': True,
                'ml_pipeline.md': True
            },
            'Archive': {
                'old_project_1.md': True,
                'old_project_2.md': True
            }
        },
        'Resources': {
            'books.md': True,
            'courses.md': True,
            'articles.md': True,
            'videos.md': True
        }
    }
    create_vault_structure(f'{base_path}/nested_notes_vault', nested_vault)
    
    # nonmd_vault - realistic mix of markdown and other files
    nonmd_md_vault = {
        'readme.md': True,
        'changelog.md': True,
        'meeting_notes.md': True,
        'project_plan.md': True,
        'ideas.md': True,
        'Assets': {
            'diagram.md': True,
            'references.md': True
        }
    }
    create_vault_structure(f'{base_path}/nonmd_md_vault', nonmd_md_vault)
    
    # Add various non-md files
    vault_path = f'{base_path}/nonmd_md_vault'
    with open(f'{vault_path}/config.json', 'w') as f:
        f.write('{"theme": "dark", "fontSize": 14}')
    with open(f'{vault_path}/todo.txt', 'w') as f:
        f.write("- [ ] Task 1\n- [ ] Task 2\n- [x] Task 3")
    with open(f'{vault_path}/script.py', 'w') as f:
        f.write('#!/usr/bin/env python3\nprint("Helper script")')
    with open(f'{vault_path}/.gitignore', 'w') as f:
        f.write('*.pyc\n__pycache__/\n.env')
    with open(f'{vault_path}/Assets/image.png', 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')  # PNG header
    with open(f'{vault_path}/Assets/data.csv', 'w') as f:
        f.write('name,value\ntest1,100\ntest2,200')
    
    # nonmd_only_vault - various non-markdown files only
    vault_path = f'{base_path}/nonmd_only_vault'
    os.makedirs(vault_path, exist_ok=True)
    
    with open(f'{vault_path}/README.txt', 'w') as f:
        f.write("This vault contains no markdown files")
    with open(f'{vault_path}/settings.yaml', 'w') as f:
        f.write('app:\n  name: test\n  version: 1.0')
    with open(f'{vault_path}/data.json', 'w') as f:
        f.write('{"users": [], "posts": []}')
    with open(f'{vault_path}/script.sh', 'w') as f:
        f.write('#!/bin/bash\necho "Hello World"')
    with open(f'{vault_path}/notes.docx', 'wb') as f:
        f.write(b'PK\x03\x04')  # DOCX header
    with open(f'{vault_path}/backup.zip', 'wb') as f:
        f.write(b'PK\x03\x04')  # ZIP header
    with open(f'{vault_path}/presentation.pptx', 'wb') as f:
        f.write(b'PK\x03\x04')  # PPTX header
    with open(f'{vault_path}/requirements.txt', 'w') as f:
        f.write('requests==2.28.0\nnumpy==1.24.0\npandas==1.5.0')
    
    print("All test vaults generated successfully!")
    print("\nVault summary:")
    print("- empty_vault: 0 notes")
    print("- single_note_vault: 1 note")
    print("- multiple_note_vault: 10 notes")
    print("- nested_notes_vault: 30+ notes in deep folder structure")
    print("- nonmd_vault: 7 .md files + 6 other file types")
    print("- nonmd_only_vault: 0 .md files, 8 other file types")

if __name__ == "__main__":
    main()