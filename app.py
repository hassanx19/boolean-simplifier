import pandas as pd
import streamlit as st
import boolean_simplifier as b

st.set_page_config(page_title="BEST - Boolean Simplifier", layout="wide")
st.title("BEST: Boolean Expression Simplification Technique")

k = int(st.number_input("Number of variables K", min_value=1,
                        max_value=b.MAX_K, value=3, step=1))
method = "kmap" if k <= 4 else "qm"
st.info(f"K = {k}: using the "
        f"{'Karnaugh Map' if method == 'kmap' else 'Quine-McCluskey'} method")

rows = [format(i, f"0{k}b") for i in range(2 ** k)]
df = pd.DataFrame({"Row": range(2 ** k),
                   **{b.LETTERS[j]: [r[j] for r in rows] for j in range(k)},
                   "F": ["0"] * (2 ** k)})
edited = st.data_editor(
    df, hide_index=True, key=f"tt_{k}",
    disabled=[c for c in df.columns if c != "F"],
    column_config={"F": st.column_config.SelectboxColumn(
        "F", options=["0", "1", "X"], required=True)})
op = list(edited["F"])

if st.button("Simplify", type="primary"):
    min_terms  = [i for i, v in enumerate(op) if v == "1"]
    dont_cares = [i for i, v in enumerate(op) if v == "X"]
    zeros      = [i for i, v in enumerate(op) if v == "0"]

    chosen, essential, primes, history = b.simplify(min_terms, dont_cares, k, method)
    comp_chosen = b.simplify(zeros, dont_cares, k, method)[0]
    sop = b.sop_string(chosen)

    st.subheader("RESULT")
    st.code(f"SOP: F = {sop}")
    st.code(f"POS: F = {b.pos_string(comp_chosen)}")
    