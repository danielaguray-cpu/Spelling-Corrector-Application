"""
spell_service.py — All 10 spelling-correction algorithms + SpellService.

Algorithms implemented:
  1. Hash Set Lookup
  2. Levenshtein Distance
  3. Damerau-Levenshtein Distance
  4. BK-Tree
  5. SymSpell (symmetric delete)
  6. N-Gram Similarity (Jaccard)
  7. Double Metaphone (full Philips rule table)
  8. Noisy Channel Model (Bayesian)
  9. Viterbi Algorithm
 10. Beam Search
"""

import math
import re
import string
from itertools import product


# ─────────────────────────────────────────────────────────────────────────────
# 1. Hash Set Lookup
# ─────────────────────────────────────────────────────────────────────────────

def hash_lookup(word: str, dictionary: set) -> bool:
    """O(1) check — returns True if word (lowercased) is in the dictionary set."""
    return word.lower() in dictionary


# ─────────────────────────────────────────────────────────────────────────────
# 2. Levenshtein Distance
# ─────────────────────────────────────────────────────────────────────────────

def levenshtein(a: str, b: str) -> int:
    """Bottom-up DP edit distance (insert, delete, substitute)."""
    a = a.lower()
    b = b.lower()
    m, n = len(a), len(b)
    # Use two-row optimisation
    prev = list(range(n + 1))
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        curr[0] = i
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev, curr = curr, [0] * (n + 1)
    return prev[n]


# ─────────────────────────────────────────────────────────────────────────────
# 3. Damerau-Levenshtein Distance (restricted — OSA)
# ─────────────────────────────────────────────────────────────────────────────

def damerau_levenshtein(a: str, b: str) -> int:
    """Restricted Damerau-Levenshtein (OSA).
    Like Levenshtein but adjacent transpositions also cost 1.
    Always damerau_levenshtein(a, b) <= levenshtein(a, b).
    """
    a = a.lower()
    b = b.lower()
    m, n = len(a), len(b)
    # d[i][j] = edit distance between a[:i] and b[:j]
    d = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,       # deletion
                d[i][j - 1] + 1,       # insertion
                d[i - 1][j - 1] + cost # substitution
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)  # transposition
    return d[m][n]


# ─────────────────────────────────────────────────────────────────────────────
# 4. BK-Tree
# ─────────────────────────────────────────────────────────────────────────────

class BKTree:
    """Metric-space tree keyed by Levenshtein distance.

    insert(word)                       — add a word
    search(word, tolerance) -> list    — words within edit distance <= tolerance
    """

    def __init__(self):
        self._root = None  # (word, {distance: child_node})

    def insert(self, word: str) -> None:
        word = word.lower()
        if self._root is None:
            self._root = (word, {})
            return
        self._insert(self._root, word)

    def _insert(self, node, word: str) -> None:
        node_word, children = node
        dist = levenshtein(node_word, word)
        if dist == 0:
            return  # duplicate
        if dist in children:
            self._insert(children[dist], word)
        else:
            children[dist] = (word, {})

    def search(self, word: str, tolerance: int) -> list:
        word = word.lower()
        if self._root is None:
            return []
        results = []
        self._search(self._root, word, tolerance, results)
        return results

    def _search(self, node, word: str, tolerance: int, results: list) -> None:
        node_word, children = node
        dist = levenshtein(node_word, word)
        if dist <= tolerance:
            results.append(node_word)
        low = max(0, dist - tolerance)
        high = dist + tolerance
        for d, child in children.items():
            if low <= d <= high:
                self._search(child, word, tolerance, results)


# ─────────────────────────────────────────────────────────────────────────────
# 5. SymSpell
# ─────────────────────────────────────────────────────────────────────────────

class SymSpell:
    """Symmetric-delete spelling correction.

    train(word_list)                   — build delete-variant index
    lookup(word, max_edit=2) -> list   — candidate original words
    """

    def __init__(self):
        # Maps derived-delete-form -> set of original words
        self._index: dict[str, set] = {}

    def _deletes(self, word: str, max_edit: int) -> set:
        """All strings reachable by 1..max_edit single-character deletions."""
        result = set()
        queue = {word}
        for _ in range(max_edit):
            next_q = set()
            for w in queue:
                for i in range(len(w)):
                    d = w[:i] + w[i + 1:]
                    if d not in result:
                        result.add(d)
                        next_q.add(d)
            queue = next_q
        return result

    def train(self, word_list: list, max_edit: int = 2) -> None:
        for word in word_list:
            word = word.lower()
            # Index the word itself
            self._index.setdefault(word, set()).add(word)
            # Index all delete variants
            for variant in self._deletes(word, max_edit):
                self._index.setdefault(variant, set()).add(word)

    def lookup(self, word: str, max_edit: int = 2) -> list:
        word = word.lower()
        candidates: set[str] = set()

        # Direct hit
        if word in self._index:
            candidates.update(self._index[word])

        # Deletes of the input word
        for variant in self._deletes(word, max_edit):
            if variant in self._index:
                candidates.update(self._index[variant])

        # Remove exact input if it is not a real dictionary word (avoid
        # returning the misspelled form as its own "suggestion")
        candidates.discard(word) if word not in self._index or word not in (
            self._index.get(word, set())
        ) else None

        return list(candidates)


# ─────────────────────────────────────────────────────────────────────────────
# 6. N-Gram Similarity (Jaccard)
# ─────────────────────────────────────────────────────────────────────────────

def ngram_similarity(a: str, b: str, n: int = 2) -> float:
    """Jaccard similarity of character n-grams.  Range [0.0, 1.0].
    ngram_similarity(s, s) == 1.0 for any non-empty s.
    """
    a, b = a.lower(), b.lower()
    if a == b:
        return 1.0
    set_a = {a[i:i + n] for i in range(len(a) - n + 1)} if len(a) >= n else {a}
    set_b = {b[i:i + n] for i in range(len(b) - n + 1)} if len(b) >= n else {b}
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def ngram_candidates(word: str, dictionary: list, n: int = 2) -> list:
    """Return words from *dictionary* sorted by descending Jaccard similarity."""
    scored = [(w, ngram_similarity(word, w, n)) for w in dictionary]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [w for w, _ in scored]


# ─────────────────────────────────────────────────────────────────────────────
# 7. Double Metaphone  (full Philips rule table — pure Python)
# ─────────────────────────────────────────────────────────────────────────────

def double_metaphone(word: str) -> tuple:  # noqa: C901 — long but required
    """Pure-Python implementation of Lawrence Philips Double Metaphone.

    Returns (primary, secondary) phonetic codes.
    double_metaphone("")[0] == ""
    double_metaphone("Smith")[0] == double_metaphone("Smyth")[0]
    """
    if not word:
        return ("", "")

    word = word.upper()
    # Pad with spaces to avoid index overruns
    word = "  " + word + "     "
    length = len(word) - 7  # effective length (excluding padding)

    # Helper – look at a slice of the padded string
    def at(idx: int, subs) -> bool:
        if isinstance(subs, str):
            subs = [subs]
        for s in subs:
            end = idx + len(s)
            if word[idx:end] == s:
                return True
        return False

    # Vowels
    VOWELS = set("AEIOUY")

    primary = []
    secondary = []
    pos = 2  # start after the two padding chars

    def add(p: str, s: str = None) -> None:
        primary.append(p)
        secondary.append(s if s is not None else p)

    # Skip silent initial letters
    if at(pos, ["GN", "KN", "PN", "AE", "WR"]):
        pos += 1

    # Initial vowels all map to 'A'
    if word[pos] in VOWELS:
        add("A")
        pos += 1

    while pos < length + 2:
        c = word[pos]

        if c in " \t":
            pos += 1
            continue

        if c in VOWELS:
            # All vowels encode to nothing except at start (handled above)
            pos += 1
            continue

        if c == "B":
            add("P")
            pos += 2 if word[pos + 1] == "B" else 1
            continue

        if c == "Ç":  # cedilla
            add("S")
            pos += 1
            continue

        if c == "C":
            # Various C rules
            if pos > 2 and not word[pos - 2] in VOWELS and at(pos - 1, "ACH") and \
               not at(pos + 2, ["I", "E"]):
                add("K")
                pos += 2
                continue
            if at(pos, "CAESAR"):
                add("S")
                pos += 2
                continue
            if at(pos, "CHIA"):
                add("K")
                pos += 2
                continue
            if at(pos, "CH"):
                if pos > 2 and at(pos, "CHAE"):
                    add("K", "X")
                    pos += 2
                    continue
                # Initial CH
                if pos == 2 and (at(pos + 2, ["AEI", "UE"]) or at(2, ["HARAC", "HARIS"])):
                    add("K")
                    pos += 2
                    continue
                if at(2, ["HOLM", "HOLZ", "MCH", "VAN ", "VON "]) or \
                   at(pos, ["ORCHES", "ARCHIT", "ORCHID"]) or \
                   at(pos + 2, ["T", "S"]) or \
                   (pos > 2 and at(pos - 2, ["A", "O", "U", "E"]) and
                    not at(pos + 2, ["L", "R", "N", "M", "B", "H", "F", "V", "W", " "])):
                    add("K")
                else:
                    if pos == 2:
                        add("X")
                    else:
                        add("X", "K")
                pos += 2
                continue
            if at(pos, "CZ") and not at(pos - 2, "WICZ"):
                add("S", "X")
                pos += 2
                continue
            if at(pos + 1, "CIA"):
                add("X")
                pos += 3
                continue
            if at(pos, "CC") and not (pos == 3 and word[2] == "M"):
                if at(pos + 2, ["I", "E", "H"]):
                    if at(pos + 2, "HU"):
                        add("K")
                    else:
                        add("X")
                    pos += 3
                else:
                    add("K")
                    pos += 2
                continue
            if at(pos, ["CK", "CG", "CQ"]):
                add("K")
                pos += 2
                continue
            if at(pos, ["CI", "CE", "CY"]):
                if at(pos, ["CIO", "CIE", "CIA"]):
                    add("S", "X")
                else:
                    add("S")
                pos += 2
                continue
            add("K")
            if at(pos + 1, " C") or at(pos + 1, " Q") or at(pos + 1, " G"):
                pos += 3
            else:
                pos += 2 if at(pos + 1, ["C", "K", "Q"]) and not at(pos + 1, ["CE", "CI"]) else 1
            continue

        if c == "D":
            if at(pos, "DG"):
                if at(pos + 2, ["I", "E", "Y"]):
                    add("J")
                    pos += 3
                else:
                    add("TK")
                    pos += 2
                continue
            if at(pos, ["DT", "DD"]):
                add("T")
                pos += 2
                continue
            add("T")
            pos += 1
            continue

        if c == "F":
            pos += 2 if word[pos + 1] == "F" else 1
            add("F")
            continue

        if c == "G":
            if word[pos + 1] == "H":
                if pos > 2 and word[pos - 1] not in VOWELS:
                    add("K")
                    pos += 2
                    continue
                if pos == 2:
                    if word[pos - 2 + 2] == "I":  # GHI at start
                        add("J")
                    else:
                        add("K")
                    pos += 2
                    continue
                if (pos > 4 and word[pos - 2] in VOWELS) or \
                   not at(pos - 3, ["B", "H", "D"]) or \
                   at(pos - 4, ["B", "H"]) or at(pos - 5, "B"):
                    pos += 2
                    continue
                pos += 2
                continue
            if word[pos + 1] == "N":
                if pos == 3 and word[2] in VOWELS:
                    add("KN", "N")
                else:
                    if not at(pos + 2, "EY") and word[pos + 1] != "Y" and \
                       word[pos - 1] not in VOWELS:
                        add("N", "KN")
                    else:
                        add("KN")
                pos += 2
                continue
            if at(pos + 1, "LI") and not at(pos, "GG"):
                add("KL", "L")
                pos += 2
                continue
            if pos == 2 and at(pos + 1, ["Y", "ES", "EP", "EB", "EL", "EY", "IB", "IL", "IN", "IE", "EI", "ER"]):
                add("K", "J")
                pos += 2
                continue
            if (at(pos + 1, ["ER", "Y"]) and
                    not at(2, ["DANGER", "RANGER", "MANGER"]) and
                    not at(pos - 1, ["E", "I"]) and
                    not at(pos - 1, ["RGY", "OGY"])):
                add("K", "J")
                pos += 2
                continue
            if at(pos + 1, ["E", "I", "Y"]) or at(pos - 1, ["AGGI", "OGGI"]):
                if at(2, ["VAN ", "VON "]) or at(2, "SCHM") or at(pos + 1, "ET"):
                    add("K")
                else:
                    if at(pos + 1, ["IER "]):
                        add("J")
                    else:
                        add("J", "K")
                pos += 2
                continue
            if word[pos + 1] == "G":
                pos += 2
            else:
                pos += 1
            add("K")
            continue

        if c == "H":
            if (at(pos, ["HAEC", "HAEM", "HAES", "HAET", "HAEV"]) or
                    (pos == 2 and at(pos + 1, "AE"))) or \
               (word[pos - 1] not in VOWELS and at(pos + 1, VOWELS)):
                add("H")
                pos += 2
            else:
                pos += 1
            continue

        if c == "J":
            if at(pos, "JOSE") or at(2, "SAN "):
                if (pos == 2 and word[pos + 4] == " ") or at(2, "SAN "):
                    add("H")
                else:
                    add("J", "H")
                pos += 1
                continue
            if pos == 2 and not at(2, "JOSE"):
                add("J", "A")
            else:
                if word[pos - 1] in VOWELS and not at(2, "JOSE") and \
                   not word[pos + 1] in VOWELS:
                    add("J", "H")
                else:
                    if word[pos + 1] == "J":
                        pass
                    else:
                        add("J")
            pos += 2 if word[pos + 1] == "J" else 1
            continue

        if c == "K":
            pos += 2 if word[pos + 1] == "K" else 1
            add("K")
            continue

        if c == "L":
            if word[pos + 1] == "L":
                if (pos == length - 3 + 2 and
                        at(pos - 1, ["ILLO", "ILLA", "ALLE"])) or \
                   (at(length - 2 + 2, ["AS", "OS"]) or
                        word[length - 1 + 2] in ["A", "O"]) and \
                   at(pos - 1, "ALLE"):
                    add("L", "")
                    pos += 2
                    continue
                pos += 2
            else:
                pos += 1
            add("L")
            continue

        if c == "M":
            if (at(pos - 1, "UMB") and
                    (pos + 1 == length + 2 or at(pos + 2, "ER"))) or \
               word[pos + 1] == "M":
                pos += 2
            else:
                pos += 1
            add("M")
            continue

        if c == "N":
            pos += 2 if word[pos + 1] == "N" else 1
            add("N")
            continue

        if c == "Ñ":
            add("N")
            pos += 1
            continue

        if c == "P":
            if word[pos + 1] == "H":
                add("F")
                pos += 2
                continue
            pos += 2 if word[pos + 1] in ["P", "B"] else 1
            add("P")
            continue

        if c == "Q":
            pos += 2 if word[pos + 1] == "Q" else 1
            add("K")
            continue

        if c == "R":
            if pos == length - 1 + 2 and not at(2, "IE") and \
               at(pos - 2, ["ME", "MA"]):
                add("", "R")
            else:
                add("R")
            pos += 2 if word[pos + 1] == "R" else 1
            continue

        if c == "S":
            if at(pos - 1, ["ISL", "YSL"]):
                pos += 1
                continue
            if pos == 2 and at(pos, "SUGAR"):
                add("X", "S")
                pos += 1
                continue
            if at(pos, "SH"):
                add("X")
                pos += 2
                continue
            if at(pos, ["SIO", "SIA"]):
                if word[pos - 1] not in VOWELS:
                    add("S", "X")
                else:
                    add("X")
                pos += 3
                continue
            if (pos == 2 and at(pos + 1, ["M", "N", "L", "W"])) or \
               at(pos + 1, "Z"):
                add("S", "X")
                pos += 2 if at(pos + 1, "Z") else 1
                continue
            if at(pos, "SC"):
                if word[pos + 2] == "H":
                    if at(pos + 3, ["OO", "ER", "EN", "UY", "ED", "EM"]):
                        add("SK")
                    else:
                        if pos == 2 and word[pos + 4] not in VOWELS and word[pos + 4] != "W":
                            add("X", "S")
                        else:
                            add("X")
                    pos += 3
                    continue
                if at(pos + 2, ["I", "E", "Y"]):
                    add("S")
                    pos += 3
                    continue
                add("SK")
                pos += 3
                continue
            if pos == length - 1 + 2 and at(pos - 2, ["AI", "OI"]):
                add("", "S")
            else:
                add("S")
            pos += 2 if word[pos + 1] in ["S", "Z"] else 1
            continue

        if c == "T":
            if at(pos, "TION"):
                add("X")
                pos += 3
                continue
            if at(pos, ["TIA", "TCH"]):
                add("X")
                pos += 3
                continue
            if at(pos, "TH") or at(pos, "TTH"):
                if at(pos + 2, ["OM", "AM"]) or at(2, ["VAN ", "VON "]) or at(2, "SCH"):
                    add("T")
                else:
                    add("0", "T")
                pos += 2
                continue
            pos += 2 if at(pos + 1, ["T", "D"]) else 1
            add("T")
            continue

        if c == "V":
            pos += 2 if word[pos + 1] == "V" else 1
            add("F")
            continue

        if c == "W":
            if at(pos, "WR"):
                add("R")
                pos += 2
                continue
            if pos == 2 and (word[pos + 1] in VOWELS or at(pos, "WH")):
                if word[pos + 1] in VOWELS:
                    add("A", "F")
                else:
                    add("A")
                pos += 1
                continue
            if (pos == length - 1 + 2 and word[pos - 1] in VOWELS) or \
               at(pos - 1, ["EWSKI", "EWSKY", "OWSKI", "OWSKY"]) or \
               at(2, "SCH"):
                add("", "F")
                pos += 1
                continue
            if at(pos, ["WICZ", "WITZ"]):
                add("TS", "FX")
                pos += 4
                continue
            pos += 1
            continue

        if c == "X":
            if not (pos == length - 1 + 2 and
                    (at(pos - 3, ["IAU", "EAU"]) or
                     at(pos - 2, ["AU", "OU"]))):
                add("KS")
            pos += 2 if at(pos + 1, ["C", "X"]) else 1
            continue

        if c == "Z":
            if word[pos + 1] == "H":
                add("J")
                pos += 2
                continue
            if at(pos + 1, ["ZO", "ZI", "ZA"]) or \
               (word[pos - 1] != "Z" and pos == length - 1 + 2):
                add("S", "TS")
            else:
                add("S")
            pos += 2 if word[pos + 1] == "Z" else 1
            continue

        pos += 1

    p = "".join(primary)[:4]
    s = "".join(secondary)[:4]
    return (p, s)


def phonetic_candidates(word: str, dictionary: list) -> list:
    """Words from *dictionary* whose double_metaphone codes overlap with *word*'s codes."""
    target_codes = set(double_metaphone(word))
    target_codes.discard("")
    if not target_codes:
        return []
    results = []
    for w in dictionary:
        codes = set(double_metaphone(w))
        codes.discard("")
        if target_codes & codes:
            results.append(w)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# 8. Noisy Channel Model (Bayesian)
# ─────────────────────────────────────────────────────────────────────────────

def noisy_channel_score(observed: str, candidate: str) -> float:
    """P(observed | candidate) proxy = exp(-damerau_levenshtein).
    Uses Damerau-Levenshtein so transpositions (common typos) score well.
    Identical strings → 1.0.  More distant → closer to 0.
    """
    dist = damerau_levenshtein(observed.lower(), candidate.lower())
    return math.exp(-dist)


def noisy_channel_best(word: str, candidates: list) -> str:
    """Return the candidate with the highest noisy_channel_score."""
    if not candidates:
        return word
    return max(candidates, key=lambda c: noisy_channel_score(word, c))


# ─────────────────────────────────────────────────────────────────────────────
# 9. Viterbi Algorithm
# ─────────────────────────────────────────────────────────────────────────────

def viterbi_correct(word: str, candidates: list) -> str:
    """One-step Viterbi lattice.
    Hidden state  = correct word
    Observation   = misspelled form (word)
    Emission prob = noisy_channel_score(word, candidate)
    Uniform prior over candidates.

    For a single observation this reduces to argmax of emission, identical to
    noisy_channel_best — by design.
    """
    if not candidates:
        return word
    # Initialise viterbi probabilities (log scale for numerical stability)
    n = len(candidates)
    prior = math.log(1.0 / n)
    viterbi = {}
    for c in candidates:
        emit = noisy_channel_score(word, c)
        viterbi[c] = prior + math.log(emit) if emit > 0 else float("-inf")
    best = max(viterbi, key=viterbi.__getitem__)
    return best


# ─────────────────────────────────────────────────────────────────────────────
# 10. Beam Search
# ─────────────────────────────────────────────────────────────────────────────

def _edit_candidates(word: str) -> set:
    """Generate all strings at edit-distance 1 from word (insert/delete/sub/transpose)."""
    letters = string.ascii_lowercase
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def beam_search_correct(word: str, dictionary: set, beam_width: int = 5) -> str:
    """Iterative single-character edits with beam pruning.

    Returns *word* immediately if already in dictionary.
    Terminates after 3 expansion steps; returns best beam candidate or original.
    """
    word_l = word.lower()
    if word_l in dictionary:
        return word_l

    # Score function: favour candidates close to the original
    def score(candidate: str) -> float:
        in_dict = 1.0 if candidate in dictionary else 0.0
        dist = levenshtein(word_l, candidate)
        return in_dict * 10.0 - dist  # dictionary hit dominates

    # Initial beam: top beam_width neighbours of the input
    initial = _edit_candidates(word_l)
    beam = sorted(initial, key=score, reverse=True)[:beam_width]

    for _ in range(3):  # max 3 expansion steps
        # Check if any beam item is in the dictionary
        for candidate in beam:
            if candidate in dictionary:
                return candidate
        # Expand beam
        next_candidates: set[str] = set()
        for b in beam:
            next_candidates.update(_edit_candidates(b))
        # Prune
        beam = sorted(next_candidates, key=score, reverse=True)[:beam_width]

    # Final check after last expansion
    for candidate in beam:
        if candidate in dictionary:
            return candidate

    # Fallback: return the closest beam item or original
    if beam:
        return beam[0]
    return word_l


# ─────────────────────────────────────────────────────────────────────────────
# SpellService
# ─────────────────────────────────────────────────────────────────────────────

class SpellService:
    """Aggregates all 10 algorithms into a single spell-correction service.

    check_word(word) -> str   — returns best correction (or word if correct)
    suggest(word)    -> list  — returns top-5 candidate corrections
    """

    def __init__(self, data_service=None):
        if data_service is None:
            from services.data_service import DataService
            data_service = DataService()
        self._data_service = data_service
        word_list: list[str] = data_service.get_all()

        # Hash set for O(1) lookup
        self._dict_set: set[str] = set(word_list)
        self._dict_list: list[str] = word_list

        # BK-Tree
        self._bk = BKTree()
        for w in word_list:
            self._bk.insert(w)

        # SymSpell
        self._sym = SymSpell()
        self._sym.train(word_list, max_edit=2)

    # ------------------------------------------------------------------ #

    def _collect_candidates(self, word: str) -> list[str]:
        """Run all candidate-generation algorithms and de-duplicate."""
        candidates: set[str] = set()

        # BK-Tree: tolerance 3 always for thorough coverage
        candidates.update(self._bk.search(word, tolerance=3))

        # SymSpell with max_edit=3 for wider reach
        candidates.update(self._sym.lookup(word, max_edit=3))

        # Bigram top 25
        ng2 = ngram_candidates(word, self._dict_list, n=2)
        candidates.update(ng2[:25])

        # Trigram top 25
        ng3 = ngram_candidates(word, self._dict_list, n=3)
        candidates.update(ng3[:25])

        # Phonetic
        candidates.update(phonetic_candidates(word, self._dict_list))

        # Beam search with wider beam
        bs = beam_search_correct(word, self._dict_set, beam_width=10)
        if bs and bs != word:
            candidates.add(bs)

        # Remove the input word itself
        candidates.discard(word)

        # Length-ratio filter: 0.4–2.5 to allow slightly longer/shorter words
        word_len = len(word)
        candidates = {
            c for c in candidates
            if word_len > 0 and 0.4 <= len(c) / word_len <= 2.5
        }

        return list(candidates)

    def _rank_candidates(self, word: str, candidates: list[str]) -> list[str]:
        """Rank by combined Damerau-Levenshtein + noisy-channel + n-gram score.

        DL is weighted most heavily so transpositions/close edits rank first.
        Prefix bonus, length penalty, and trigram similarity are used as
        additional signals.
        """
        if not candidates:
            return []

        def combined_score(c: str) -> float:
            dl = damerau_levenshtein(word, c)
            lv = levenshtein(word, c)
            nc = noisy_channel_score(word, c)
            ng2 = ngram_similarity(word, c, n=2)
            ng3 = ngram_similarity(word, c, n=3)

            # Length similarity penalty: penalize candidates very different in length
            len_diff = abs(len(word) - len(c))
            length_penalty = 0.1 * len_diff

            # Strong DL=1 bonus: these are almost certainly the right correction
            dl1_bonus = 0.5 if dl == 1 else 0.0

            # Transposition bonus
            transposition_bonus = 0.3 if dl < lv else 0.0

            # Prefix bonus: reward words that start with the same letter(s)
            prefix_bonus = 0.2 if (word and c and word[0] == c[0]) else 0.0
            if len(word) >= 2 and len(c) >= 2 and word[:2] == c[:2]:
                prefix_bonus += 0.15

            return (nc + dl1_bonus + transposition_bonus + prefix_bonus
                    + 0.15 * ng2 + 0.1 * ng3 - 0.4 * dl - length_penalty)

        ranked = sorted(candidates, key=combined_score, reverse=True)
        return ranked

    # ------------------------------------------------------------------ #

    def check_word(self, word: str) -> str:
        """Return best correction for *word*, or *word* itself if already correct."""
        # 1. Strip leading/trailing punctuation; if nothing left, return as-is
        clean = word.strip(string.punctuation)
        if not clean:
            return word

        clean_l = clean.lower()

        # 2. Hash-set short-circuit
        if hash_lookup(clean_l, self._dict_set):
            return clean_l

        # 3. Collect & rank candidates
        candidates = self._collect_candidates(clean_l)
        if not candidates:
            return clean_l

        ranked = self._rank_candidates(clean_l, candidates)

        # 4. If top candidate is too far away, it's likely a proper noun or
        #    intentional word — return original unchanged
        if ranked and damerau_levenshtein(clean_l, ranked[0]) > 3:
            return clean_l

        # 5. Viterbi picks the winner from the top candidates
        top = ranked[:15]
        return viterbi_correct(clean_l, top)

    def suggest(self, word: str) -> list:
        """Return top-15 correction suggestions, or [] if word is in dictionary."""
        clean = word.strip(string.punctuation)
        if not clean:
            return []

        clean_l = clean.lower()

        if hash_lookup(clean_l, self._dict_set):
            return []

        candidates = self._collect_candidates(clean_l)
        if not candidates:
            return []

        ranked = self._rank_candidates(clean_l, candidates)

        # Allow DL <= 5 so phonetically/structurally similar alternatives
        # all appear (e.g. "speak", "spill", "spell" for "speal")
        ranked = [c for c in ranked if damerau_levenshtein(clean_l, c) <= 5]

        return ranked[:15]
