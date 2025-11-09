"""
This UI is taking alot of time to do. needed alot of help from LLM back and forth to fix stuff and orginize it for me

"""


# generic Popups

from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult


class ConfirmModal(ModalScreen[bool]):
    """Generic confirmation modal"""

    def __init__(self, message: str, title: str = "Confirm"):
        super().__init__()
        self.message = message
        self.title_text = title
        
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.title_text, id="title")
            yield Label(self.message, id="message")
            
            with Horizontal(id="buttons"):
                yield Button("Yes", id="yes", variant="error")
                yield Button("No", id="no", variant="default")
                
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)


class InputModal(ModalScreen[str | None]):
    """Generic input modal"""

    def __init__(self, title: str, prompt: str, placeholder: str = ""):
        super().__init__()
        self.title_text = title
        self.prompt_text = prompt
        self.placeholder_text = placeholder
        
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.title_text, id="title")
            yield Label(self.prompt_text, id="prompt")
            yield Input(placeholder=self.placeholder_text, id="input")
            yield Label("", id="error")
            
            with Horizontal(id="buttons"):
                yield Button("OK", id="ok", variant="success")
                yield Button("Cancel", id="cancel")
                
    def on_mount(self):
        self.query_one(Input).focus()
        
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok":
            input_value = self.query_one(Input).value.strip()
            
            if not input_value:
                self.query_one("#error", Label).update("Input cannot be empty")
                return
                
            self.dismiss(input_value)
        else:
            self.dismiss(None)
            
    def on_input_submitted(self, event: Input.Submitted):
        """Handle Enter key"""
        self.query_one("#ok", Button).press()


#Vault Screen

from textual.screen import Screen
from textual.widgets import OptionList, Input, Static, Header, Footer
from textual.containers import Vertical, Center, Horizontal
from textual.binding import Binding
from textual.app import ComposeResult
from pathlib import Path
import os

class VaultPage(Screen):
    """Vault selection page with keyboard-driven interface"""

    BINDINGS = [
        ("ctrl+o", "open_vault", "Open"), 
        ("ctrl+n", "new_vault", "New"),
        ("ctrl+d", "delete_vault", "Delete"), 
        ("ctrl+r", "refresh", "Refresh"),
        ("ctrl+q", "quit_app", "Quit"),
    ]
    
    def __init__(self, vaults_config_path: Path):
        super().__init__()
        self.vaults_config_path = vaults_config_path
        self.vault_paths = []
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Center():
            with Vertical(id="vault_chooser"):
                yield Static("📚 Select Vault", id="vault_label")
                yield OptionList(id="vault_list")
                yield Input(placeholder="Search vaults...", id="vault_search")
                
    def on_mount(self):
        self.load_vaults()
        self.refresh_vault_list()
        self.query_one(Input).focus()
        
    def load_vaults(self):
        if self.vaults_config_path.exists():
            try:
                with open(self.vaults_config_path, 'r') as f:
                    self.vault_paths = [line.strip() for line in f if line.strip()]
            except Exception as e:
                self.notify(f"Error: {e}", severity="error")
                self.vault_paths = []
        else:
            self.vault_paths = []
            
    def save_vaults(self):
        try:
            self.vaults_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.vaults_config_path, 'w') as f:
                for path in self.vault_paths:
                    f.write(f"{path}\n")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")
            
    def refresh_vault_list(self):
        opt_list = self.query_one(OptionList)
        opt_list.clear_options()
        
        if self.vault_paths:
            for vault_path in self.vault_paths:
                path = Path(vault_path)
                exists = path.exists() and path.is_dir()
                status = "✓" if exists else "✗"
                opt_list.add_option(f"{status} {path.name}")
                
    def on_input_changed(self, event: Input.Changed):
        query = event.value.lower().strip()
        filtered = [p for p in self.vault_paths if query in Path(p).name.lower()] if query else self.vault_paths
        
        opt_list = self.query_one(OptionList)
        opt_list.clear_options()
        
        if filtered:
            for vault_path in filtered:
                path = Path(vault_path)
                exists = path.exists() and path.is_dir()
                status = "✓" if exists else "✗"
                opt_list.add_option(f"{status} {path.name}")
                
    def on_input_submitted(self, event: Input.Submitted):
        opt_list = self.query_one(OptionList)
        if opt_list.option_count > 0:
            opt_list.highlighted = 0
            self.action_open_vault()
            
    def on_option_list_option_selected(self, event):
        self.action_open_vault()
        
    def get_selected_vault_path(self) -> str | None:
        opt_list = self.query_one(OptionList)
        if opt_list.highlighted is None or not self.vault_paths:
            return None
        
        query = self.query_one(Input).value.lower().strip()
        filtered = [p for p in self.vault_paths if query in Path(p).name.lower()] if query else self.vault_paths
            
        if 0 <= opt_list.highlighted < len(filtered):
            return filtered[opt_list.highlighted]
        return None
        
    def action_open_vault(self):
        vault_path = self.get_selected_vault_path()
        if not vault_path:
            self.notify("No vault selected", severity="warning")
            return
            
        path = Path(vault_path)
        if not path.exists() or not path.is_dir():
            self.notify("Vault path no longer exists!", severity="error")
            return
            
        try:
            from vault import Vault
            vault = Vault(vault_path)
            self.app.push_screen(NotesScreen(vault))
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")
            
    def action_new_vault(self):
        """Create a new vault folder"""
        def on_create(vault_path: str | None):
            if not vault_path or not vault_path.strip():
                return
            vault_path = vault_path.strip()
            path = Path(vault_path)
            
            # Check if path already exists
            if path.exists():
                self.notify("Path already exists!", severity="error")
                return
            
            # Try to create the directory
            try:
                path.mkdir(parents=True, exist_ok=False)
                
                # Add to vault list
                vault_path_str = str(path.absolute())
                if vault_path_str not in self.vault_paths:
                    self.vault_paths.append(vault_path_str)
                    self.save_vaults()
                    self.refresh_vault_list()
                    self.notify(f"Created vault: {path.name}")
                    self.query_one(Input).focus()
                else:
                    self.notify("Vault already in list!", severity="warning")
                    
            except PermissionError:
                self.notify("Permission denied to create folder!", severity="error")
            except Exception as e:
                self.notify(f"Error creating vault: {e}", severity="error")
                    
        self.app.push_screen(
            InputModal(
                "Create New Vault", 
                "Enter path for new vault folder:", 
                "/path/to/new-vault"
            ), 
            on_create
        )
        
    def action_delete_vault(self):
        vault_path = self.get_selected_vault_path()
        if not vault_path:
            self.notify("No vault selected", severity="warning")
            return
        
        vault_name = Path(vault_path).name
        
        def on_confirm(confirmed: bool):
            if confirmed:
                self.vault_paths.remove(vault_path)
                self.save_vaults()
                self.refresh_vault_list()
                self.notify(f"Removed: {vault_name}")
                self.query_one(Input).focus()
                    
        self.app.push_screen(ConfirmModal(f"Remove '{vault_name}'?\n(Files NOT deleted)", "⚠️  Confirm"), on_confirm)
        
    def action_refresh(self):
        self.load_vaults()
        self.refresh_vault_list()
        self.notify("Refreshed")
        self.query_one(Input).focus()
        
    def action_quit_app(self):
        self.app.exit()


# note editing/viewing screen

from textual.widgets import DirectoryTree, TextArea, Markdown, Static
from note_io import write_note, read_note
from note import Note


class EditorPanel(Vertical):
    """Markdown editor panel"""

    def compose(self) -> ComposeResult:
        yield Label("📝 Editor", classes="panel-title")
        yield TextArea(id="editor", language="markdown")
        
    def get_text(self) -> str:
        """Get current editor content"""
        return self.query_one(TextArea).text
        
    def set_text(self, text: str):
        """Set editor content"""
        self.query_one(TextArea).text = text


class ViewerPanel(Vertical):
    """Markdown viewer panel"""

    
    def compose(self) -> ComposeResult:
        yield Label("👁️ Viewer", classes="panel-title")
        yield Markdown(id="viewer")
        
    def set_markdown(self, text: str):
        """Set markdown content to render"""
        self.query_one(Markdown).update(text)


class StatsPanel(Vertical):
    """Note statistics panel"""

    def compose(self) -> ComposeResult:
        yield Label("📊 Stats", classes="panel-title")
        yield Static(id="stats-content")
        
    def set_stats(self, note: Note):
        """Display note statistics"""
        if not note or not note.raw_md:
            self.query_one("#stats-content").update("[dim]No note loaded[/dim]")
            return
            
        # Calculate stats
        content = note.raw_md
        words = len(content.split())
        chars = len(content)
        lines = content.count('\n') + 1
        
        # Build stats display
        stats_text = f"""[bold]Title:[/bold] {note.title}

[bold]Tags:[/bold] {', '.join(note.tags) if note.tags else '[dim]none[/dim]'}

[bold]Created:[/bold] {note.created_date.strftime('%Y-%m-%d %H:%M')}
[bold]Modified:[/bold] {note.modified_date.strftime('%Y-%m-%d %H:%M')}

[bold]Words:[/bold] {words:,}
[bold]Characters:[/bold] {chars:,}
[bold]Lines:[/bold] {lines:,}
"""
        
        self.query_one("#stats-content").update(stats_text)


class NotesScreen(Screen):
    """Main notes interface"""

    BINDINGS = [
        Binding("ctrl+n", "new_note", "New Note"),
        Binding("ctrl+d", "delete_note", "Delete Note"),
        Binding("ctrl+s", "save_note", "Save Note"),
        Binding("ctrl+r", "refresh_vault", "Refresh Vault"),
        Binding("ctrl+b", "toggle_tree", "Toggle Tree"),
        Binding("ctrl+w", "close_vault", "Close Vault"),
        Binding("f1", "toggle_panel('editor')", "Editor"),
        Binding("f2", "toggle_panel('viewer')", "Viewer"),
        Binding("f3", "toggle_panel('stats')", "Stats"),
    ]
    

    def __init__(self, vault):
        """
        Args:
            vault: Your Vault instance
        """
        super().__init__()
        self.vault = vault
        self.current_note_path = None  # Relative path
        self.tree_visible = True
        self.active_panels = {"editor", "viewer"}  # Start with these
        
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal(id="main_layout"):
            # Tree container
            with Vertical(id="tree_container"):
                yield Label(f"📂 {Path(self.vault.root_path).name}", id="vault_name")
                yield DirectoryTree(self.vault.root_path, id="tree")
                
            # Panel container - mount default panels here
            with Horizontal(id="panel_container"):
                yield EditorPanel().add_class("panel")
                yield ViewerPanel().add_class("panel")
            
        yield Label("", id="status_bar")
        yield Footer()
        
    def on_mount(self):
        # Configure tree to show only .md files
        tree = self.query_one(DirectoryTree)
        tree.show_root = False
        tree.show_guides = True
        
        # Panels are already mounted in compose
        self.active_panels = {"editor", "viewer"}
        
        self.update_status("Ready")
        
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        """User selected a file in tree"""
        file_path = Path(event.path)
        
        # Only handle .md files
        if file_path.suffix != '.md':
            return
            
        # Get relative path
        relative_path = os.path.relpath(file_path, self.vault.root_path)
        
        try:
            # Load note using your vault
            self.vault.refresh_single(relative_path)
            
            if relative_path in self.vault.notes:
                self.current_note_path = relative_path
                self.update_all_panels()
                self.update_status(f"Loaded: {file_path.name}")
            else:
                self.notify("Failed to load note", severity="error")
                
        except Exception as e:
            self.notify(f"Error loading note: {e}", severity="error")
            
    def action_new_note(self):
        """Create new note or folder"""
        def on_create(input_text: str | None):
            if not input_text:
                return
                
            input_text = input_text.strip()
            
            # Check if creating a folder (ends with /)
            if input_text.endswith('/'):
                folder_path = input_text.rstrip('/')
                full_folder_path = os.path.join(self.vault.root_path, folder_path)
                
                try:
                    os.makedirs(full_folder_path, exist_ok=True)
                    
                    # Refresh vault and tree
                    self.vault.refresh()
                    tree = self.query_one(DirectoryTree)
                    tree.reload()
                    
                    self.update_status(f"Created folder: {folder_path}")
                    self.notify(f"Created folder: {folder_path}", severity="information")
                    
                except Exception as e:
                    self.notify(f"Error creating folder: {e}", severity="error")
                    
                return
            
            # Creating a note file
            filename = input_text
            
            # Ensure .md extension
            if not filename.endswith('.md'):
                filename += '.md'
            
            # Check if path contains folders
            if '/' in filename or '\\' in filename:
                # Split into folder and filename
                path_parts = filename.replace('\\', '/').split('/')
                note_filename = path_parts[-1]
                folder_path = '/'.join(path_parts[:-1])
                
                # Create folder if it doesn't exist
                full_folder_path = os.path.join(self.vault.root_path, folder_path)
                os.makedirs(full_folder_path, exist_ok=True)
                
                # Full note path (relative)
                relative_note_path = filename
            else:
                # Simple filename in root
                relative_note_path = filename
                note_filename = filename
            
            # Full absolute path
            note_path = os.path.join(self.vault.root_path, relative_note_path)
            
            if os.path.exists(note_path):
                self.notify("Note already exists!", severity="error")
                return
                
            try:
                # Create title from filename
                title = note_filename.replace('.md', '').replace('-', ' ').replace('_', ' ').title()
                
                # Create Note object with just title and body
                note = Note(f"# {title}\n\n")
                note.title = title
                
                # Use Note's formatter to create the file
                formatted_md = note.get_formatted_md()
                
                # Write using note_io
                write_note(self.vault.root_path, relative_note_path, formatted_md)
                
                # Refresh vault
                self.vault.refresh()
                
                # Load new note
                self.current_note_path = relative_note_path
                self.update_all_panels()
                
                # Refresh tree
                tree = self.query_one(DirectoryTree)
                tree.reload()
                
                self.update_status(f"Created: {relative_note_path}")
                self.notify(f"Created note: {relative_note_path}", severity="information")
                
            except Exception as e:
                self.notify(f"Error creating note: {e}", severity="error")
                
        self.app.push_screen(
            InputModal(
                title="Create New Note/Folder",
                prompt="Enter path (end with / for folder):",
                placeholder="folder/my-note.md or folder/"
            ),
            callback=on_create
        )
        
    def action_delete_note(self):
        """Delete current note"""
        if not self.current_note_path:
            self.notify("No note selected", severity="warning")
            return
            
        note_name = Path(self.current_note_path).name
        
        def on_confirm(confirmed: bool):
            if confirmed:
                try:
                    # Delete file
                    note_path = os.path.join(self.vault.root_path, self.current_note_path)
                    os.remove(note_path)
                    
                    # Refresh vault
                    self.vault.refresh()
                    
                    # Clear current note
                    self.current_note_path = None
                    self.update_all_panels()
                    
                    # Refresh tree
                    tree = self.query_one(DirectoryTree)
                    tree.reload()
                    
                    self.update_status(f"Deleted: {note_name}")
                    self.notify(f"Deleted note: {note_name}", severity="information")
                    
                except Exception as e:
                    self.notify(f"Error deleting note: {e}", severity="error")
                    
        self.app.push_screen(
            ConfirmModal(
                message=f"Delete note '{note_name}'?\nThis cannot be undone!",
                title="⚠️  Confirm Deletion"
            ),
            callback=on_confirm
        )
        
    def action_save_note(self):
        """Save current note - preserves cursor position"""
        if not self.current_note_path:
            self.notify("No note to save", severity="warning")
            return
            
        # Get content from editor
        if "editor" not in self.active_panels:
            self.notify("Editor panel not open", severity="warning")
            return
            
        editor = self.get_panel_instance(EditorPanel)
        if not editor:
            return
            
        try:
            # Save cursor position BEFORE updating
            text_area = editor.query_one(TextArea)
            saved_cursor = text_area.selection
            
            # Get raw markdown from editor
            content = editor.get_text()
            
            # Parse into Note to update metadata
            note = Note(content)
            
            # Update modified date
            from datetime import datetime
            note.modified_date = datetime.now().replace(microsecond=0)
            
            # Get formatted markdown with updated metadata
            formatted_md = note.get_formatted_md()
            
            # Write using note_io
            write_note(self.vault.root_path, self.current_note_path, formatted_md)
            
            # Refresh this note in vault
            self.vault.refresh_single(self.current_note_path)
            
            # Update all panels
            self.update_all_panels()
            
            # Restore cursor position AFTER updating
            text_area = editor.query_one(TextArea)
            text_area.selection = saved_cursor
            
            self.update_status("Saved!")
            self.notify("Note saved!", severity="information")
            
        except Exception as e:
            self.notify(f"Error saving note: {e}", severity="error")
            
    def action_refresh_vault(self):
        """Refresh vault and reload current note"""
        try:
            self.vault.refresh()
            
            if self.current_note_path:
                self.update_all_panels()
                
            # Refresh tree
            tree = self.query_one(DirectoryTree)
            tree.reload()
            
            self.update_status("Vault refreshed")
            self.notify("Vault refreshed", severity="information")
            
        except Exception as e:
            self.notify(f"Error refreshing: {e}", severity="error")
            
    def action_toggle_tree(self):
        """Show/hide directory tree"""
        tree_container = self.query_one("#tree_container")
        
        if self.tree_visible:
            tree_container.add_class("hidden")
            self.tree_visible = False
            self.update_status("Tree hidden")
        else:
            tree_container.remove_class("hidden")
            self.tree_visible = True
            self.update_status("Tree visible")
            
    def action_close_vault(self):
        """Return to vault chooser"""
        self.app.pop_screen()
        
    def action_toggle_panel(self, panel_type: str):
        """Toggle panel visibility"""
        if panel_type in self.active_panels:
            self.remove_panel(panel_type)
            self.update_status(f"{panel_type.title()} panel hidden")
        else:
            self.add_panel(panel_type)
            self.update_status(f"{panel_type.title()} panel shown")
            
    def add_panel(self, panel_type: str):
        """Add panel to container"""
        if panel_type in self.active_panels:
            return
            
        container = self.query_one("#panel_container")
        
        if panel_type == "editor":
            panel = EditorPanel()
        elif panel_type == "viewer":
            panel = ViewerPanel()
        elif panel_type == "stats":
            panel = StatsPanel()
        else:
            return
            
        panel.add_class("panel")
        container.mount(panel)
        self.active_panels.add(panel_type)
        
        # Update with current note if exists
        if self.current_note_path:
            self.update_panel(panel)
            
    def remove_panel(self, panel_type: str):
        """Remove panel from container"""
        if panel_type not in self.active_panels:
            return
            
        # Find and remove panel
        for panel in self.query(".panel"):
            if (isinstance(panel, EditorPanel) and panel_type == "editor") or \
               (isinstance(panel, ViewerPanel) and panel_type == "viewer") or \
               (isinstance(panel, StatsPanel) and panel_type == "stats"):
                panel.remove()
                self.active_panels.remove(panel_type)
                break
                
    def update_all_panels(self):
        """Update all active panels with current note"""
        for panel in self.query(".panel"):
            self.update_panel(panel)
            
    def update_panel(self, panel):
        """Update specific panel with current note data"""
        if not self.current_note_path:
            # No note loaded
            if isinstance(panel, EditorPanel):
                panel.set_text("")
            elif isinstance(panel, ViewerPanel):
                panel.set_markdown("[dim]No note selected[/dim]")
            elif isinstance(panel, StatsPanel):
                panel.set_stats(None)
            return
            
        # Get note from vault
        if self.current_note_path not in self.vault.notes:
            return
            
        note = self.vault.notes[self.current_note_path]
        
        if isinstance(panel, EditorPanel):
            # Show raw markdown in editor
            panel.set_text(note.raw_md)
            
        elif isinstance(panel, ViewerPanel):
            # Show rendered markdown in viewer
            panel.set_markdown(note.body)
            
        elif isinstance(panel, StatsPanel):
            # Show stats
            panel.set_stats(note)
            
    def get_panel_instance(self, panel_class):
        """Get instance of specific panel type"""
        for panel in self.query(".panel"):
            if isinstance(panel, panel_class):
                return panel
        return None
        
    def update_status(self, message: str):
        """Update status bar"""
        status = self.query_one("#status_bar")
        
        # Show current note and message
        if self.current_note_path:
            status.update(f"📄 {self.current_note_path} | {message}")
        else:
            status.update(message)


# main app

from textual.app import App

class OnyxNotesApp(App):
    """Main application"""
    
    CSS_PATH = "style.tcss"  # Update this to your CSS path
    
    def __init__(self):
        super().__init__()
        
        # Config path for vault list
        self.vaults_config = Path.home() / ".config" / "onyx-notes" / "vaults.txt"
        
    def on_mount(self):
        # Start with vault chooser
        self.push_screen(VaultPage(self.vaults_config))


# ===== RUN =====

if __name__ == "__main__":
    app = OnyxNotesApp()
    app.run()