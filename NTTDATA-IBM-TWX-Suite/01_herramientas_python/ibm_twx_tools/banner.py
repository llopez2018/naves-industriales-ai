"""NTTDATA terminal banner — ASCII art logo + suite info."""

# ANSI
_B  = "\033[94m"   # blue
_LB = "\033[96m"   # cyan (light blue)
_W  = "\033[97m"   # white
_DM = "\033[2m"    # dim
_BD = "\033[1m"    # bold
_RS = "\033[0m"    # reset

# ── Shonai mark (concentric circles + water drop) ──────────────────────────
_SYM = [
    r"   ╭──────╮   ",
    r"  ╱ ╭────╮ ╲  ",
    r" │  │  ◉  │  │",
    r" │  ╰────╯  │ ",
    r"  ╲         ╱ ",
    r"   ╰──────╯   ",
]

# ── "NTT DATA" block letters ────────────────────────────────────────────────
_TXT = [
    r"███╗  ██╗ ████████╗████████╗  ██████╗  █████╗ ████████╗ █████╗ ",
    r"████╗ ██║ ╚══██╔══╝╚══██╔══╝  ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗",
    r"██╔████╗██║   ██║      ██║    ██║  ██║███████║   ██║   ███████║ ",
    r"██║╚═██╗██║   ██║      ██║    ██║  ██║██╔══██║   ██║   ██╔══██║ ",
    r"██║  ╚████║   ██║      ██║    ██████╔╝██║  ██║   ██║   ██║  ██║ ",
    r"╚═╝   ╚═══╝   ╚═╝      ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝",
]

_GAP = "  "


def _visible_len(s: str) -> int:
    """Approx visible length — strips ANSI, counts each char as 1 column."""
    import re
    return len(re.sub(r"\033\[[0-9;]*m", "", s))


def get_banner(version: str = "1.0.0", suite: str = "IBM TWX Reverse Engineering Suite") -> str:
    rows = [f"{sym}{_GAP}{txt}" for sym, txt in zip(_SYM, _TXT)]
    inner_w = max(_visible_len(r) for r in rows) + 4   # 2 left + 2 right padding

    top    = f"╔{'═' * inner_w}╗"
    bottom = f"╚{'═' * inner_w}╝"
    blank  = f"║{' ' * inner_w}║"

    sub  = f"  {suite}  ·  v{version}"
    corp = "  Corporate: NTT DATA  ·  Powered by Claude AI"

    def _row(content: str) -> str:
        pad = inner_w - _visible_len(content) - 2
        return f"║  {content}{' ' * max(pad, 0)}║"

    lines = [
        "",
        f"{_B}{_BD}{top}{_RS}",
        f"{_B}{_BD}{blank}{_RS}",
    ]
    for r in rows:
        sym_part, _, txt_part = r.partition(_GAP)
        colored = f"{_B}{_BD}{sym_part}{_RS}{_GAP}{_LB}{_BD}{txt_part}{_RS}"
        # raw row for padding calc
        pad = inner_w - _visible_len(r) - 2
        lines.append(f"{_B}{_BD}║{_RS}  {_B}{_BD}{sym_part}{_RS}{_GAP}{_LB}{_BD}{txt_part}{_RS}{' ' * max(pad, 0)}{_B}{_BD}║{_RS}")

    lines += [
        f"{_B}{_BD}{blank}{_RS}",
        f"{_B}{_BD}{_row(sub)}{_RS}",
        f"{_B}{_DM}{_row(corp)}{_RS}",
        f"{_B}{_BD}{blank}{_RS}",
        f"{_B}{_BD}{bottom}{_RS}",
        "",
    ]
    return "\n".join(lines)


def print_banner(version: str = "1.0.0", suite: str = "IBM TWX Reverse Engineering Suite") -> None:
    import sys
    print(get_banner(version, suite), file=sys.stderr)


# ── Compact one-liner for Copilot markdown ──────────────────────────────────
COPILOT_HEADER = (
    "```\n"
    "   ╭──────╮   ███╗  ██╗████████╗████████╗  ██████╗  █████╗ ████████╗ █████╗\n"
    "  ╱ ╭────╮ ╲  ████╗ ██║╚══██╔══╝╚══██╔══╝  ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗\n"
    " │  │  ◉  │ │ ██╔████╗██║   ██║      ██║   ██║  ██║███████║   ██║   ███████║\n"
    " │  ╰────╯  │ ██║╚═██╗██║   ██║      ██║   ██║  ██║██╔══██║   ██║   ██╔══██║\n"
    "  ╲         ╱  ██║  ╚████║   ██║      ██║   ██████╔╝██║  ██║   ██║   ██║  ██║\n"
    "   ╰──────╯   ╚═╝   ╚═══╝   ╚═╝      ╚═╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝\n"
    "```\n"
)
