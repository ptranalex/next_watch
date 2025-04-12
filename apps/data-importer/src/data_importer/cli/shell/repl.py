"""REPL configuration for the data_importer shell."""

import os
from typing import Any, Dict


def configure_repl(
    embed: Any,
    namespace: Dict[str, Any],
    theme: str = "monokai",
    quiet: bool = False,
    plain: bool = False,
) -> None:
    """Configure and launch a ptpython REPL.

    Args:
        embed: The ptpython embed function
        namespace: Dictionary of objects to include in the namespace
        theme: The color theme to use
        quiet: Whether to suppress non-essential output
        plain: Whether to use plain output without syntax highlighting
    """

    ***REMOVED*** Define a configuration function for the REPL
    def configure_instance(repl: Any) -> None:
        ***REMOVED*** Enable autocompletion explicitly (fix for missing autocompletion)
        repl.enable_auto_suggest = True
        repl.enable_open_in_editor = True
        repl.enable_history_search = True
        repl.enable_input_validation = True
        repl.enable_system_bindings = True
        repl.complete_while_typing = True

        ***REMOVED*** Theme configuration
        if not plain and theme != "default":
            try:
                ***REMOVED*** Set style by name if it exists
                repl.use_code_colorscheme(theme)
            except Exception:
                ***REMOVED*** Fall back to default if theme not found
                pass
        elif plain:
            ***REMOVED*** Use a very minimal style if plain mode is requested
            repl.use_code_colorscheme("default")
            repl.color_depth = "DEPTH_1_BIT"  ***REMOVED*** Minimal colors

        ***REMOVED*** Common configurations
        repl.highlight_matching_parenthesis = True
        repl.show_status_bar = True
        repl.show_signature = True
        repl.show_docstring = True
        ***REMOVED*** Pop-up menus are preferred over completion-toolbar for better UX
        repl.completion_visualisation = "pop-up"
        repl.show_line_numbers = True
        repl.insert_blank_line_after_output = True
        repl.completion_menu_scroll_offset = 0  ***REMOVED*** Start at the top

    ***REMOVED*** Launch the REPL with our configuration
    embed(
        globals=namespace,
        history_filename=os.path.expanduser("~/.data_importer_history"),
        title="Data Importer Shell",
        configure=configure_instance,
    )
