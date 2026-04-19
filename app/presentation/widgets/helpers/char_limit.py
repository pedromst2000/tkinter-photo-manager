import tkinter as tk

from app.presentation.styles.colors import colors


def validate_entry_char_limit(
    entry: tk.Entry,
    count_label: tk.Label,
    limit: int,
    required: bool = True,
) -> None:
    """
    Update character counter and visual feedback for a single tk.Entry widget.

    Args:
        entry: The Entry widget to validate.
        count_label: Label displaying the character count.
        limit: Maximum allowed character count.
        required: If True, show required-color when field is empty.
    """
    value = entry.get().strip()
    length = len(value)

    count_label.config(text=f"{length}/{limit}")

    default_fg = colors["secondary-500"]
    danger_fg = colors.get("danger-500")
    required_fg = colors.get("required-500")

    if required and length == 0:
        count_label.config(fg=required_fg)
        entry.config(highlightthickness=2, highlightbackground=required_fg)
    elif length > limit:
        count_label.config(fg=danger_fg)
        entry.config(highlightthickness=2, highlightbackground=danger_fg)
    else:
        count_label.config(fg=default_fg)
        entry.config(highlightthickness=0)


def validate_text_char_limit(
    text_widget: tk.Text,
    count_label: tk.Label,
    limit: int,
    required: bool = True,
) -> None:
    """
    Update character counter and visual feedback for a tk.Text widget.

    Args:
        text_widget: The Text widget to validate (e.g. ScrollableText.text).
        count_label: Label displaying the character count.
        limit: Maximum allowed character count.
        required: If True, show required-color when field is empty.
    """
    value = text_widget.get("1.0", "end-1c").strip()
    length = len(value)

    count_label.config(text=f"{length}/{limit}")

    default_fg = colors["secondary-500"]
    danger_fg = colors.get("danger-500")
    required_fg = colors.get("required-500")

    if required and length == 0:
        count_label.config(fg=required_fg)
        try:
            text_widget.config(highlightthickness=2, highlightbackground=required_fg)
        except Exception:
            pass
    elif length > limit:
        count_label.config(fg=danger_fg)
        try:
            text_widget.config(highlightthickness=2, highlightbackground=danger_fg)
        except Exception:
            pass
    else:
        count_label.config(fg=default_fg)
        try:
            text_widget.config(highlightthickness=0)
        except Exception:
            pass
