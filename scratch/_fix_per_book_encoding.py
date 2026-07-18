from pathlib import Path

p = Path(__file__).resolve().parents[1] / "engine" / "per_book_predictions.py"
lines = p.read_bytes().splitlines()
out = []
for line in lines:
    if line.strip().startswith(b'"""Correct reading from Manoj'):
        out.append(b'    """Chart-based answer (lagna-specific); shared across all books."""')
    else:
        out.append(line)
p.write_bytes(b"\n".join(out) + b"\n")
print("fixed", p)
