#TUI to interact with note taking
#TODO list:
"""
main panels:
Esc = select vault (can select vaults by number or clicking)
edit note panel (editable) : have 1 hidable pane (notes tree) and 3 openable panes (edit note , show note, metadata) (default show note tree pane on the left and temp note saying 'Start editing by selecting a note or create a note by clicking N')
g =graph panel 

popups:
n = new note popup
o = open note popup (can open notes by double clicking a note in note tree)
d = delete note popup (by default will select the note opened)
t = edit tags of opened note (show in edit note panel and graph panel)
alt - t = edit all tags

graph panel:
show a legend of top tags by color (can click a tag to highlight the notes with this tag)

total shortcuts = [Esc , g , n , o , d , t ]
"""
#idea add a class for errors that will display in cli or TUI

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DirectoryTree, Input, OptionList, Static
from textual.containers import HorizontalGroup, VerticalScroll , Container, Vertical , Center
from textual.message import Message


class GraphPanel(HorizontalGroup):
    def compose(self) -> ComposeResult:
        pass

class VaultPanel(Container):
    def __init__(self, vaults: dict):
        super().__init__()
        self.all_vaults = vaults  # {path: name} or just list of paths
        
    def compose(self) -> ComposeResult:

        yield Static("Select Vault:", classes="label", id="vault_label")
        yield OptionList(*self.all_vaults.keys(), id="vault_list")
        yield Input(placeholder="Search vaults...", id="vault_search")
    
    def on_mount(self):
        """Focus search input on load."""
        self.query_one("#vault_search", Input).focus()
    
    def on_input_changed(self, event: Input.Changed):
        """Filter vault list as user types."""
        if event.input.id != "vault_search":
            return
            
        query = event.value.lower()
        option_list = self.query_one("#vault_list", OptionList)
        
        # Filter vaults
        filtered = filter(lambda x: query in x.lower(),self.all_vaults.keys()) if query else list(self.all_vaults.keys())
        
        # Update options
        option_list.clear_options()
        if filtered:
            option_list.add_options(filtered)
    
    def on_input_submitted(self, event: Input.Submitted):
        """When user presses Enter in search, select first option."""
        if event.input.id != "vault_search":
            return
            
        option_list = self.query_one("#vault_list", OptionList)
        if option_list.option_count > 0:
            # Highlight first option
            option_list.highlighted = 0
            # Trigger selection
            option_list.action_select()
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        """Handle vault selection."""
        selected_vault = str(event.option.prompt)
        self.post_message(self.VaultSelected(selected_vault))
    
    class VaultSelected(Message):
        """Message sent when vault is selected."""
        def __init__(self, vault_path: str):
            self.vault_path = vault_path
            super().__init__()


class NotePanel(HorizontalGroup):
    def compose(self) -> ComposeResult:
        pass




class NoteTakingApp(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [("n","new_note","New note"),
                ("d", "toggle_dark", "Toggle dark mode"),
                ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        vaults = {
            "notes": "Personal Notes",
            "work": "Work Vault",
            "projects": "Projects"
        }
        with Center():
            yield VaultPanel(vaults)


    def on_vault_panel_vault_selected(self, event: VaultPanel.VaultSelected):
        """Handle vault selection at app level."""

        self.notify(f"Selected: {event.vault_path} Vault")
        # Open vault, switch screens, etc.

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

if __name__ == "__main__":
    NoteTakingApp().run()

