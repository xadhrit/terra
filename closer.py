from src.instagram import Instagram
import argparse
import sys
import signal
from rich.console import Console 
from src.twitter import Twitter

pc = Console()


is_windows = False

try:
    import gnureadline
except:
    is_windows = True
    import pyreadline

    
def main():
    pc.print("  WELCOME TO THE MAIN MENU OF CLOSER:-)   ", style="yellow")


