"""REPL configuration for the data_importer shell."""

from typing import Any


def configure_repl(
    repl: Any,
    theme: str = "monokai",
    plain: bool = False,
) -> None:
    """Configure a ptpython REPL instance.

    Args:
        repl: The ptpython REPL instance to configure
        theme: The color theme to use
        plain: Whether to use plain output without syntax highlighting
    """
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
