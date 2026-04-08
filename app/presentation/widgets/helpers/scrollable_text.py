import tkinter as tk
import tkinter.font as tkfont
from typing import Optional


class ScrollableText(tk.Frame):
    """A Text widget with a permanently-visible vertical scrollbar.

    The scrollbar is always shown and properly linked to the text widget.
    Use ``scrollable_text.text`` to read/write content.

    Usage:
        s = ScrollableText(parent, width=40, height=10, font=..., bg=..., fg=...)
        s.pack()
        content = s.text.get("1.0", "end-1c")
    """

    def __init__(
        self,
        parent,
        width: int = 40,
        height: int = 8,
        font: Optional[tkfont.Font] = None,
        bg: Optional[str] = None,
        fg: Optional[str] = None,
        wrap: str = "word",
        **text_kwargs,
    ):
        super().__init__(
            parent, bg=bg or parent.cget("bg")
        )  # inherit bg if not specified

        self.vscroll = tk.Scrollbar(self, orient="vertical")
        self.vscroll.pack(side="right", fill="y")

        self.text = tk.Text(
            self,
            width=width,
            height=height,
            font=font,
            bg=bg or parent.cget("bg"),
            fg=fg or parent.cget("fg"),
            wrap=wrap,
            yscrollcommand=self.vscroll.set,
            **text_kwargs,
        )
        self.text.pack(side="left", fill="both", expand=True)

        self.vscroll.config(command=self.text.yview)
