import collections
import subprocess

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()

with Live(Panel(Text("")), console=console, auto_refresh=False, transient=True) as live:
    process = subprocess.Popen(
        "ping -c3 1.1.1.1",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        universal_newlines=True,
    )

    # Create a deque with a max length of 10
    last_lines = collections.deque(maxlen=10)

    for line in process.stdout:
        last_lines.append(line.rstrip())
        live.update(Panel(Text("\n".join(last_lines))))
        live.refresh()
console.print(process.wait())
