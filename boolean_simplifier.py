"""
BEST: Boolean Expression Simplification Technique
-------------------------------------------------
K <= 4  -> Karnaugh Map method
K  > 4  -> Quine-McCluskey (QM) method
"""

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MAX_K = 8          # entering 2^K rows by hand gets painful beyond this
DASH = "_"         # symbol for an eliminated variable


# ---------------------------------------------------------------- 1. INPUT
def read_k():
    """Keep asking until the user enters an integer from 1 to MAX_K."""
    while True:
        try:
            k = int(input(f"Enter the number of variables K (1-{MAX_K}): "))
            if 1 <= k <= MAX_K:
                return k
            print(f"ERROR: K must be between 1 and {MAX_K}.")
        except ValueError:
            print("ERROR: please enter a whole number.")


def read_truth_table(k):
    """Ask for the output of every row. Returns (op, min_terms, dont_cares)."""
    op, min_terms, dont_cares = [], [], []
    names = " ".join(LETTERS[:k]) #names of variables taken from the LETTERS
    print(f"\nInputs are in the order: {names}")
    for i in range(2 ** k):
        row = " ".join(format(i, f"0{k}b"))
        y = input(f"  Row {i:>3}  [{row}]  output (0/1/X): ").strip().upper()
        while y not in ("0", "1", "X"):
            y = input("    Invalid. Enter 0, 1 or X: ").strip().upper()
        op.append(y)
        if y == "1":
            min_terms.append(i)
        elif y == "X":
            dont_cares.append(i)
    return op, min_terms, dont_cares


# ------------------------------------------------------- 2. QUINE-McCLUSKEY
def group_by_ones(terms, k):
    """{number_of_ones: [(pattern, {minterm}), ...]}"""
    groups = {}
    for t in terms:
        pattern = format(t, f"0{k}b")
        groups.setdefault(pattern.count("1"), []).append((pattern, {t}))
    return groups


def combine(t1, t2):
    """Merge two (pattern, set) tuples if they differ in exactly one real bit.
    Returns (new_pattern, union_of_sets) or None."""
    p1, p2 = t1[0], t2[0]
    pos, diff = -1, 0
    for i in range(len(p1)):
        if p1[i] != p2[i]:
            if p1[i] == DASH or p2[i] == DASH:   # dashes must line up
                return None
            diff += 1
            pos = i
    if diff != 1:
        return None
    return (p1[:pos] + DASH + p1[pos + 1:], t1[1] | t2[1])


def qm_round(groups):
    """One QM round. Returns (new_groups, used_patterns, primes_found)."""
    new_groups, used = {}, set()
    for ones in groups:
        if ones + 1 not in groups:               # only truly adjacent groups
            continue
        for x in groups[ones]:
            for y in groups[ones + 1]:
                merged = combine(x, y)
                if merged is not None:
                    used.add(x[0])
                    used.add(y[0])
                    bucket = new_groups.setdefault(merged[0].count("1"), [])
                    if merged not in bucket:     # avoid duplicate terms
                        bucket.append(merged)
    primes = [t for ones in groups for t in groups[ones] if t[0] not in used]
    return new_groups, used, primes


def quine_mccluskey(min_terms, dont_cares, k):
    """Returns (prime_implicants, history).
    history = list of (table, used_patterns) so the tables can be displayed."""
    groups = group_by_ones(min_terms + dont_cares, k)
    prime_implicants, history = [], []
    while groups:
        new_groups, used, primes = qm_round(groups)
        history.append((groups, used))
        prime_implicants += primes
        groups = new_groups
    return prime_implicants, history


# ------------------------------------------------------------ 3. K-MAP
def gray_code(n):
    """Gray code of n bits as integers: n=2 -> [0, 1, 3, 2]."""
    return [i ^ (i >> 1) for i in range(2 ** n)]


def kmap_layout(k):
    """First k//2 variables label the rows, the rest label the columns."""
    row_bits = k // 2
    col_bits = k - row_bits
    return row_bits, col_bits, gray_code(row_bits), gray_code(col_bits)


def kmap_cell(r, c, col_bits, row_gray, col_gray):
    """Minterm number sitting at grid position (r, c)."""
    return (row_gray[r] << col_bits) | col_gray[c]


def _sizes(n):
    s = 1
    while s <= n:
        yield s
        s *= 2


def kmap_groups(min_terms, dont_cares, k):
    """Find all MAXIMAL rectangular groups (sizes 1,2,4,8,16, edges wrap
    around) made only of 1s and X's. Returns a list of (pattern, set)."""
    row_bits, col_bits, rg, cg = kmap_layout(k)
    rows, cols = 2 ** row_bits, 2 ** col_bits
    allowed = set(min_terms) | set(dont_cares)

    candidates = set()
    for h in _sizes(rows):
        for w in _sizes(cols):
            for r0 in range(rows):
                for c0 in range(cols):
                    cells = frozenset(
                        kmap_cell((r0 + i) % rows, (c0 + j) % cols,
                                  col_bits, rg, cg)
                        for i in range(h) for j in range(w))
                    if cells <= allowed:
                        candidates.add(cells)

    # keep only groups that are not inside a bigger valid group
    maximal = [g for g in candidates if not any(g < other for other in candidates)]

    result = []
    for g in maximal:
        pattern = ""
        for bit in range(k):
            values = {(m >> (k - 1 - bit)) & 1 for m in g}
            pattern += DASH if len(values) == 2 else str(values.pop())
        result.append((pattern, set(g)))
    return sorted(result, key=lambda t: t[0])


# --------------------------------------------------- 4. CHOOSING THE ANSWER
def select_primes(primes, min_terms):
    """Prime implicant chart: essential primes first, then greedy cover.
    Don't-cares are NOT required to be covered.
    Returns (chosen, essential)."""
    uncovered = set(min_terms)
    chosen, essential = [], []

    for m in sorted(min_terms):
        covering = [p for p in primes if m in p[1]]
        if len(covering) == 1 and covering[0] not in chosen:
            chosen.append(covering[0])
            essential.append(covering[0])
    for p in chosen:
        uncovered -= p[1]

    while uncovered:                       # greedy: most new coverage wins,
        best = max(primes, key=lambda p: (len(p[1] & uncovered),   # ties ->
                                          p[0].count(DASH)))       # fewer literals
        chosen.append(best)
        uncovered -= best[1]
    return chosen, essential


def simplify(min_terms, dont_cares, k, method):
    """Full pipeline for one function. Returns (chosen, essential, primes, history)."""
    if not min_terms:
        return [], [], [], []
    if method == "kmap":
        primes, history = kmap_groups(min_terms, dont_cares, k), []
    else:
        primes, history = quine_mccluskey(min_terms, dont_cares, k)
    chosen, essential = select_primes(primes, min_terms)
    return chosen, essential, primes, history


# ------------------------------------------------------- 5. EXPRESSIONS
def literals(pattern):
    """'01_' -> [('A', True... )]  as (letter, is_true) pairs; dashes skipped."""
    return [(LETTERS[i], ch == "1") for i, ch in enumerate(pattern) if ch != DASH]


def pattern_to_term(pattern):
    """'01_' -> "A'B" """
    lits = literals(pattern)
    if not lits:
        return "1"
    return "".join(l if t else l + "'" for l, t in lits)


def sop_string(chosen):
    if not chosen:
        return "0"
    if any(all(ch == DASH for ch in p[0]) for p in chosen):
        return "1"
    return " + ".join(pattern_to_term(p[0]) for p in chosen)


def pos_string(chosen_of_complement):
    """Product-of-sums for F, built from the SOP of F' (De Morgan)."""
    if not chosen_of_complement:
        return "1"
    if any(all(ch == DASH for ch in p[0]) for p in chosen_of_complement):
        return "0"
    sums = []
    for p, _ in chosen_of_complement:
        sums.append("(" + " + ".join(l + "'" if t else l
                                     for l, t in literals(p)) + ")")
    return "".join(sums)


def nand_form(chosen):
    """SOP -> two-level NAND-NAND:  F = NAND( NAND(term1), NAND(term2), ... )"""
    inner = []
    for p, _ in chosen:
        lits = ", ".join(l if t else l + "'" for l, t in literals(p))
        inner.append(f"NAND({lits})")
    return "F = NAND( " + ", ".join(inner) + " )"


def nor_form(chosen_of_complement):
    """POS -> two-level NOR-NOR:  F = NOR( NOR(sum1), NOR(sum2), ... )"""
    inner = []
    for p, _ in chosen_of_complement:
        lits = ", ".join(l + "'" if t else l for l, t in literals(p))
        inner.append(f"NOR({lits})")
    return "F = NOR( " + ", ".join(inner) + " )"


# ------------------------------------------------------- 6. VERIFICATION
def verify(chosen, op, k):
    """Check the simplified expression against EVERY row of the truth table."""
    for row, expected in enumerate(op):
        if expected == "X":
            continue
        bits = format(row, f"0{k}b")
        value = any(all(pc in (DASH, b) for pc, b in zip(p, bits))
                    for p, _ in chosen)
        if value != (expected == "1"):
            return False
    return True


# ---------------------------------------------------------- 7. DISPLAY
def print_qm_tables(history, k):
    print("\n--- Quine-McCluskey tables (✓ = merged into a bigger term) ---")
    for n, (table, used) in enumerate(history):
        print(f"\nTable {n}:")
        print(f"  {'Ones':<5}{'Minterms':<22}{'Pattern':<{k + 3}}Used")
        for ones in sorted(table):
            for pattern, covered in table[ones]:
                mt = ",".join(map(str, sorted(covered)))
                mark = "✓" if pattern in used else "(prime)"
                print(f"  {ones:<5}{mt:<22}{pattern:<{k + 3}}{mark}")


def print_prime_chart(primes, min_terms, chosen):
    """Text version of the prime implicant chart."""
    print("\n--- Prime implicant chart (X = covers that minterm) ---")
    width = 4
    header = f"{'Prime':<12}" + "".join(f"{m:>{width}}" for m in min_terms)
    print(header)
    for p, covered in sorted(primes, key=lambda t: t[0]):
        cells = "".join(f"{('X' if m in covered else '.'):>{width}}"
                        for m in min_terms)
        star = " <- chosen" if any(p == c[0] for c in chosen) else ""
        print(f"{p:<12}{cells}{star}")


def print_kmap(op, k):
    row_bits, col_bits, rg, cg = kmap_layout(k)
    row_vars = LETTERS[:row_bits]
    col_vars = LETTERS[row_bits:k]
    print(f"\n--- K-map (rows: {row_vars or '-'}, columns: {col_vars}) ---")
    corner = f"{row_vars}\\{col_vars}"
    print(f"{corner:>8} | " + "  ".join(format(c, f"0{col_bits}b") for c in cg))
    print("-" * (11 + 4 * len(cg)))
    for r in range(len(rg)):
        label = format(rg[r], f"0{row_bits}b") if row_bits else "-"
        cells = "  ".join(f"{op[kmap_cell(r, c, col_bits, rg, cg)]:>{col_bits}}"
                          for c in range(len(cg)))
        print(f"{label:>8} | {cells}")


def print_groups(chosen, essential):
    print("\n--- Groups chosen ---")
    for p, covered in chosen:
        kind = "essential" if any(p == e[0] for e in essential) else "extra"
        print(f"  {p}  covers {sorted(covered)}  ->  {pattern_to_term(p)}  ({kind})")


def main():
    print("WELCOME TO BEST: BOOLEAN EXPRESSION SIMPLIFICATION TECHNIQUE\n")
    k = read_k()
    op, min_terms, dont_cares = read_truth_table(k)
    zeros = [i for i, v in enumerate(op) if v == "0"]
    method = "kmap" if k <= 4 else "qm"

    print("\n--- Truth table ---")
    print(f"{' '.join(LETTERS[:k])} | F")
    for i, v in enumerate(op):
        print(f"{' '.join(format(i, f'0{k}b'))} | {v}")
    print(f"\nMinterms   : {min_terms}")
    print(f"Don't cares: {dont_cares}")
    print(f"Method     : {'Karnaugh Map' if method == 'kmap' else 'Quine-McCluskey'}")

    # ---- simplify F (SOP)
    chosen, essential, primes, history = simplify(min_terms, dont_cares, k, method)

    if method == "kmap":
        print_kmap(op, k)
    else:
        print_qm_tables(history, k)
    if primes:
        if method == "qm":
            print_prime_chart(primes, min_terms, chosen)
        print_groups(chosen, essential)

    # ---- simplify F' (needed for POS and the NOR-only form)
    comp_chosen = simplify(zeros, dont_cares, k, method)[0]

    sop = sop_string(chosen)
    print("\n=========== RESULT ===========")
    print(f"Simplified SOP : F = {sop}")
    print(f"Simplified POS : F = {pos_string(comp_chosen)}")

    if sop in ("0", "1"):
        print(f"\nF is the constant {sop}, so no gates are needed.")
    else:
        print("\n--- Gate-level forms ---")
        print("AND-OR-NOT :", "F = " + " + ".join(
            "AND(" + ", ".join(l if t else f"NOT({l})" for l, t in literals(p[0])) + ")"
            for p in chosen))
        print("NAND only  :", nand_form(chosen))
        print("             (a complemented input X' is built as NAND(X, X))")
        print("NOR only   :", nor_form(comp_chosen))
        print("             (a complemented input X' is built as NOR(X, X))")

    ok = verify(chosen, op, k)
    print("\nSelf-check against the truth table:", "PASSED ✓" if ok else "FAILED ✗")


if __name__ == "__main__":
    main()