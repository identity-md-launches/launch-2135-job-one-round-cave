"""Tiny offline demonstration of the citation-trail handoff."""
from pathlib import Path

def main():
    stones = [(12, 4), (18, 4), (24, 4)]
    passage = (4, 6)
    print(f"stones={stones}; checked_passage_lines={passage[0]}-{passage[1]}")

if __name__ == "__main__":
    main()
