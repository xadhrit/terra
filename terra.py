import argparse
import sys
import signal
from rich.console import Console 
from src.twittr import Twitter
from src.instagram import Instagram

pc = Console()

""" 
First Check if os is windows or unix based
"""

is_windows = False

try:
    import gnureadline
except:
    is_windows = True
    import pyreadline

    
def main():
    pc.print("   TERRA 2025   ", style="yellow")


if __name__ == "__main__":
    main()

