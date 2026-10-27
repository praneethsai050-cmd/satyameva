"""
seed.py
Seeds Satyameva Aegis with the 4 production roles and JUIT Waknaghat credentials.
Removes legacy demo accounts.
"""

import argparse
import sys
from scripts.setup_clean_portals import setup_portals

def seed(reset: bool = False):
    setup_portals(reset=reset)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seed Satyameva with clean portals and JUIT credentials')
    parser.add_argument('--reset', action='store_true', help='Reset the database and blockchain before seeding')
    args = parser.parse_args()
    seed(reset=args.reset)
