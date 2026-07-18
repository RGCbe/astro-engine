# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(r"F:\astro\engine\event_narrative.py")
text = path.read_text(encoding="utf-8")

# Fix corrupted dicts by replacing lines 13-39 block
old_block_start = text.index("SOURCE_TA = {")
old_block_end = text.index("HOUSE_GAIN = {")
new_header = '''SOURCE_TA = {
    "salary": "\\u0baa\\u0b9f\\u0bcd\\u0b9a\\u0bbf / \\u0b89\\u0baf\\u0bb0\\u0bcd\\u0bb5\\u0bc1",
    "business": "\\u0bb5\\u0ba3\\u0bbf\\u0b95 / \\u0ba4\\u0bca\\u0bb4\\u0bbf\\u0bb2\\u0bcd",
    "land": "\\u0ba8\\u0bbf\\u0bb2\\u0bae\\u0bcd / \\u0b9a\\u0bca\\u0ba4\\u0bcd\\u0ba4\\u0bc1",
    "rental": "\\u0bb5\\u0bbe\\u0b9f\\u0b95\\u0bc8 \\u0bb5\\u0bb0\\u0bc1\\u0bae\\u0bbe\\u0ba9\\u0bae\\u0bcd",
    "inheritance": "\\u0baa\\u0bbe\\u0bb0\\u0b9a\\u0bc1 / \\u0b95\\u0bc1\\u0b9f\\u0bc1\\u0bae\\u0bcd\\u0baa\\u0bae\\u0bcd",
    "spouse": "\\u0b9a\\u0bc1\\u0ba4\\u0bbf / \\u0baa\\u0ba4\\u0bcd\\u0ba9\\u0bbf",
    "network": "\\u0b8e\\u0ba4\\u0bbf\\u0bb0\\u0bcd / \\u0b95\\u0bc1\\u0bb1\\u0bbf\\u0baa\\u0bcd\\u0baa\\u0bc1",
    "speculation": "\\u0b9a\\u0bc1\\u0baa\\u0bcd\\u0baa\\u0bc1\\u0bb1\\u0bc1\\u0bb5\\u0bc1 / \\u0baa\\u0b99\\u0bcd\\u0b95\\u0bc1",
    "father": "\\u0ba4\\u0ba8\\u0bcd\\u0ba4\\u0bc8 / \\u0b95\\u0bc1\\u0bb0\\u0bc1",
    "grace": "\\u0b95\\u0bc1\\u0bb0\\u0bc1 \\u0b85\\u0ba9\\u0bc1\\u0b95\\u0bcd\\u0b95\\u0bbf\\u0bb0\\u0b95\\u0bae\\u0bcd",
    "education": "\\u0bb5\\u0bbf\\u0ba4\\u0bcd\\u0ba4\\u0bbf\\u0baf\\u0bbe\\u0b9a\\u0bae\\u0bcd",
    "foreign": "\\u0bb5\\u0bc6\\u0bb3\\u0bbf\\u0ba8\\u0bbe\\u0b9f\\u0bc1",
}

MECHANISM_TA = {
    "legal": "\\u0b9a\\u0b9f\\u0bcd\\u0b9f\\u0bc1 / \\u0bb5\\u0bb0\\u0bbf \\u0bb5\\u0bb4\\u0b95\\u0bcd\\u0b95\\u0bc1",
    "medical": "\\u0b86\\u0bb0\\u0bcb\\u0b95 \\u0b9a\\u0bc6\\u0bb2\\u0bb5\\u0bc1",
    "job_loss": "\\u0bb\\u0bc7\\u0bb2\\u0bc8 \\u0b87\\u0bb4\\u0baa\\u0bcd\\u0baa\\u0bc1",
    "partnership": "\\u0b95\\u0bc2\\u0b9f\\u0bcd\\u0b9f\\u0bc1 \\u0b89\\u0b9f\\u0bc8\\u0bb5\\u0bc1",
    "fraud": "\\u0b8e\\u0bb0\\u0bbf / \\u0bb0\\u0bbe\\u0b95\\u0bc1",
    "family_expense": "\\u0b95\\u0bc1\\u0b9f\\u0bc1\\u0bae\\u0bcd\\u0baa \\u0b9a\\u0bc6\\u0bb2\\u0bb5\\u0bc1",
    "market": "\\u0b9a\\u0ba8\\u0bcd\\u0ba4\\u0bc8 \\u0b87\\u0bb4\\u0baa\\u0bcd\\u0baa\\u0bc1",
    "delay": "\\u0b9a\\u0ba9\\u0bbf \\u0ba4\\u0bbe\\u0bae\\u0ba4\\u0bae\\u0bcd",
    "sudden": "8\\u0bb5\\u0ba4\\u0bc1 \\u0ba4\\u0bbf\\u0b9f\\u0bc0\\u0bb0\\u0bcd \\u0b87\\u0bb4\\u0baa\\u0bcd\\u0baa\\u0bc1",
    "abroad_drain": "12\\u0bb5\\u0ba4\\u0bc1 \\u0bb5\\u0bc6\\u0bb3\\u0bbf\\u0ba8\\u0bbe\\u0b9f\\u0bc1 \\u0b9a\\u0bc6\\u0bb2\\u0bb5\\u0bc1",
}

'''
new_header = new_header.encode("utf-8").decode("unicode_escape")
text = text[:old_block_start] + new_header + text[old_block_end:]

text = text.replace(
    'DISCLAIMER_TA = (\n    "\\u0b95????? \\u0b85??????? \\u2014 \\u0b89???? \\u0b87????."\n)',
    'DISCLAIMER_TA = "\\u0b95\\u0ba3\\u0bbf\\u0ba4\\u0bcd\\u0ba4 \\u0b85\\u0ba9\\u0bc1\\u0bae\\u0bbe\\u0ba9\\u0bae\\u0bcd \\u2014 \\u0b89\\u0bb1\\u0bc1\\u0ba4\\u0bbf \\u0b87\\u0bb2\\u0bcd\\u0bb2\\u0bc8."',
)
text = text.encode("utf-8").decode("unicode_escape") if False else text

# Fix client_ta f-strings - use ascii labels only in generated client lines to avoid corruption
text = text.replace(
    """        client_ta = (
            f"\\u0b87?????: {_tags_line(mechanism_tags, 'ta') or '\\u0b9a????'} "
            f"({mech_line[:50]}). {DISCLAIMER_TA}"
        )""",
    """        client_ta = (
            f"\\u0b87\\u0bb4\\u0baa\\u0bcd\\u0baa\\u0bc1: {_tags_line(mechanism_tags, 'ta') or '\\u0b9a\\u0bc6\\u0bb2\\u0bb5\\u0bc1'} "
            f"({mech_line[:50]}). {DISCLAIMER_TA}"
        )""",
)
text = text.replace(
    """        client_ta = (
            f"\\u0bb5???????: {_tags_line(source_tags, 'ta') or '\\u0b9a??????'} "
            f"({src_line[:50]}). {DISCLAIMER_TA}"
        )""",
    """        client_ta = (
            f"\\u0bb5\\u0bb0\\u0bc1\\u0bae\\u0bbe\\u0ba9\\u0bae\\u0bcd: {_tags_line(source_tags, 'ta') or '\\u0b9a\\u0bc6\\u0bb2\\u0bcd\\u0bb5\\u0bae\\u0bcd'} "
            f"({src_line[:50]}). {DISCLAIMER_TA}"
        )""",
)

# Apply unicode_escape to disclaimer replacement
import re
text = re.sub(
    r'DISCLAIMER_TA = .*?\n\)',
    'DISCLAIMER_TA = "\u0b95\u0ba3\u0bbf\u0ba4\u0bcd\u0ba4 \u0b85\u0ba9\u0bc1\u0bae\u0bbe\u0ba9\u0bae\u0bcd \u2014 \u0b89\u0bb1\u0bc1\u0ba4\u0bbf \u0b87\u0bb2\u0bcd\u0bb2\u0bc8."\n',
    text,
    count=1,
)

for pair in [
    (r'f"\\u0b87\?+\?:', 'f"\u0b87\u0bb4\u0baa\u0bcd\u0baa\u0bc1:'),
    (r"or '\\u0b9a\?+'", "or '\u0b9a\u0bc6\u0bb2\u0bb5\u0bc1'"),
    (r'f"\\u0bb5\?+\?:', 'f"\u0bb5\u0bb0\u0bc1\u0bae\u0bbe\u0ba9\u0bae\u0bcd:'),
    (r"or '\\u0b9a\?+'", "or '\u0b9a\u0bc6\u0bb2\u0bcd\u0bb5\u0bae\u0bcd'", 1),
]:
    pass

path.write_text(text, encoding="utf-8")
print("fixed", path)
