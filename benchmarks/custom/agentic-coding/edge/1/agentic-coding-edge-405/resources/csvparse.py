"""Small CSV parser for the ingest pipeline (BUGGY naive version)."""


def parse_csv(text):
    """Parse CSV text into a list of rows (each a list of field strings)."""
    if text == "":
        return []
    rows = []
    for line in text.strip().split("\n"):
        rows.append([f.strip() for f in line.split(",")])
    return rows
