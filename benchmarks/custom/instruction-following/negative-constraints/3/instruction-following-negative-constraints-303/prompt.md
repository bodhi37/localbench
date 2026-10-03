# Constrained inscription

A plaque is to be carved. You must compose its inscription from a fixed word
list: `resources/vocabulary.txt` in this task folder contains one word per line
(all words are capital letters, A–Z only). Every word you use must be one of
those lines, copied exactly.

The inscription must satisfy **all** of these rules at once:

1. It is exactly **4 lines** long, and each line contains exactly **7 words**.
2. Words are separated by single spaces. No line may be empty, and no word may
   be repeated anywhere in the inscription (each of the 28 words is distinct).
3. No word in the inscription may contain the letter **E**. (Some entries in the
   vocabulary do contain `E`; those entries may not be used.)
4. The words `TOPAZ`, `QUILL` and `MAROON` must each appear exactly once.
5. Each line must contain exactly **one** word that contains the letter **Z**.
6. In each line, the first word and the last word must **not** begin with the
   same letter.

## Output contract

Your entire response must be exactly those 4 lines, in order, and nothing else —
no preamble, no explanation, no numbering, no punctuation, no trailing text, no
blank lines. The whole response is graded, so a single extra character makes it
wrong.