"""
Quantum Circuit Partitioning Explorer
======================================
Algorithms: Brute Force | Spectral | Kernighan-Lin | Hypergraph (KaHyPar-style)

Run:     streamlit run quantum_partitioning_app.py
Install: pip install streamlit qiskit qiskit-aer networkx matplotlib numpy
"""

import streamlit as st
import random, time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from itertools import combinations

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from networkx.algorithms.community import kernighan_lin_bisection

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Quantum Circuit Partitioning",
    page_icon="⚛️",
    layout="wide",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #0a0e1a; color: #e2e8f0; }

.hero {
    background: linear-gradient(135deg, #0f1b35 0%, #0a2040 50%, #0d1a30 100%);
    border: 1px solid #1e3a5f; border-radius: 16px;
    padding: 2.5rem 3rem; margin-bottom: 2rem; position: relative; overflow: hidden;
}
.hero h1 { font-size:2.2rem; font-weight:700; color:#fff; margin:0 0 .5rem; letter-spacing:-.5px; }
.hero p  { color:#7ea8c9; font-size:1rem; margin:0; }
.hero .accent { color:#38b6ff; }

.metric-row { display:flex; gap:1rem; margin:1rem 0; flex-wrap:wrap; }
.metric-card {
    background:#111827; border:1px solid #1e3a5f;
    border-radius:10px; padding:1rem 1.4rem; flex:1; min-width:120px;
}
.metric-card .label { font-size:.7rem; color:#5a7fa0; text-transform:uppercase;
    letter-spacing:1px; font-family:'JetBrains Mono',monospace; }
.metric-card .value { font-size:1.7rem; font-weight:700; color:#38b6ff;
    font-family:'JetBrains Mono',monospace; line-height:1.2; }

.section-header {
    font-size:1.05rem; font-weight:600; color:#cbd5e1;
    border-left:3px solid #38b6ff; padding-left:.75rem;
    margin:1.8rem 0 1rem;
}
.algo-card {
    background:#111827; border:1px solid #1e3a5f;
    border-radius:12px; padding:1.2rem; margin-bottom:.8rem;
}
.algo-card .algo-name { font-size:.72rem; color:#5a7fa0; text-transform:uppercase;
    letter-spacing:1px; font-family:'JetBrains Mono',monospace; }
.algo-card .algo-cuts { font-size:2rem; font-weight:700;
    font-family:'JetBrains Mono',monospace; line-height:1.1; }
.algo-card .algo-time { font-size:.75rem; color:#5a7fa0;
    font-family:'JetBrains Mono',monospace; }

.result-table { width:100%; border-collapse:collapse;
    font-family:'JetBrains Mono',monospace; font-size:.82rem; }
.result-table th { background:#1a2744; color:#7ea8c9; padding:.6rem 1rem;
    text-align:left; font-size:.7rem; letter-spacing:.8px; text-transform:uppercase; }
.result-table td { padding:.55rem 1rem; border-bottom:1px solid #1a2744; color:#cbd5e1; }
.result-table tr:hover td { background:#111827; }
.best-row td { color:#38b6ff !important; font-weight:600; }
.tag-best { background:#0a2a4a; color:#38b6ff; border:1px solid #38b6ff;
    border-radius:4px; padding:1px 6px; font-size:.68rem; }
.tag-cat  { background:#1a1a2e; color:#a78bfa; border:1px solid #a78bfa;
    border-radius:4px; padding:1px 6px; font-size:.65rem; margin-left:4px; }

.noise-bar-wrap { margin:.5rem 0; }
.noise-label { font-size:.75rem; color:#7ea8c9; margin-bottom:3px;
    font-family:'JetBrains Mono',monospace; }
.noise-bar-bg  { background:#1a2744; border-radius:4px; height:10px; }
.noise-bar-fill{ height:10px; border-radius:4px; }

.info-box { background:#0a1f35; border:1px solid #1e4a6e; border-radius:8px;
    padding:.9rem 1.2rem; margin:.8rem 0; font-size:.83rem;
    color:#7ea8c9; font-family:'JetBrains Mono',monospace; }

[data-testid="stSidebar"] { background:#0d1120 !important; border-right:1px solid #1e3a5f; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color:#7ea8c9 !important; }
.stButton>button {
    background:linear-gradient(135deg,#1a56db,#0ea5e9); color:white; border:none;
    border-radius:8px; font-family:'Space Grotesk',sans-serif;
    font-weight:600; font-size:.95rem; padding:.6rem 1.8rem; width:100%;
}
.stButton>button:hover { opacity:.88; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>⚛️ Quantum Circuit <span class="accent">Partitioning</span> Explorer</h1>
  <p>Compare <strong>Brute Force · Spectral · Kernighan-Lin · Hypergraph Partitioning</strong></p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Circuit Settings")
    min_q = st.slider("Min qubits", 4, 8,  4)
    max_q = st.slider("Max qubits", 6, 14, 10)
    min_d = st.slider("Min depth",  3, 8,  4)
    max_d = st.slider("Max depth",  6, 20, 10)

    st.markdown("---")
    st.markdown("### 🔊 Noise Settings")
    err1 = st.select_slider("Single-qubit error", [0.0001,0.001,0.005,0.01], value=0.001)
    err2 = st.select_slider("Two-qubit error",    [0.001, 0.005,0.01, 0.05], value=0.01)

    st.markdown("---")
    st.markdown("### 🧮 Algorithms")
    run_bf = st.checkbox("Brute Force",           value=True, help="Exhaustive baseline")
    run_sp = st.checkbox("Spectral",              value=True, help="Fiedler vector bisection")
    run_kl = st.checkbox("Kernighan-Lin",         value=True, help="Iterative swap improvement")
    run_hg = st.checkbox("KaHyPar", value=True, help="Hyperedge-aware partitioning")

    st.markdown("---")
    generate = st.button(" Generate & Run")

ALGO_META = {
    "Brute Force":  {"color": "#38b6ff", "cat": "Optimal"},
    "Spectral":     {"color": "#a78bfa", "cat": "Graph"},
    "Kernighan-Lin":{"color": "#34d399", "cat": "Graph"},
    "KaHyPar":   {"color": "#ec4899", "cat": "Hypergraph"},
}

# ─────────────────────────────────────────────
# Circuit generation
# ─────────────────────────────────────────────
def generate_random_circuit(min_q, max_q, min_d, max_d):
    seed = random.randint(0, 99999)
    random.seed(seed); np.random.seed(seed)
    n = random.randint(min_q, max_q)
    d = random.randint(min_d, max_d)
    qc = QuantumCircuit(n)
    sg = ['h','x','y','z','rx','ry','rz']
    tg = ['cx','cz']
    for _ in range(d):
        for q in range(n):
            g = random.choice(sg)
            if g in ['rx','ry','rz']:
                getattr(qc, g)(np.random.uniform(0, 2*np.pi), q)
            else:
                getattr(qc, g)(q)
        qs = random.sample(range(n), n)
        for i in range(0, n-1, 2):
            getattr(qc, random.choice(tg))(qs[i], qs[i+1])
    return qc, seed

# ─────────────────────────────────────────────
# Graph building
# ─────────────────────────────────────────────
def circuit_to_graph(qc):
    G = nx.Graph()
    for q in range(qc.num_qubits):
        G.add_node(q)
    for inst in qc.data:
        if len(inst.qubits) == 2:
            q0 = qc.qubits.index(inst.qubits[0])
            q1 = qc.qubits.index(inst.qubits[1])
            if G.has_edge(q0, q1):
                G[q0][q1]['weight'] += 1
                G[q0][q1]['gate']   += '+' + inst.operation.name
            else:
                G.add_edge(q0, q1, weight=1, gate=inst.operation.name)
    return G

def circuit_to_hypergraph(qc):
    """
    Hypergraph: each unique multi-qubit gate instance is a hyperedge.
    Returns list of hyperedges (each is a set of qubit indices).
    """
    hyperedges = []
    for inst in qc.data:
        if len(inst.qubits) >= 2:
            idxs = tuple(qc.qubits.index(q) for q in inst.qubits)
            hyperedges.append(idxs)
    return hyperedges

# ─────────────────────────────────────────────
# Partition helpers
# ─────────────────────────────────────────────
def count_cuts(G, part):
    return sum(1 for u,v in G.edges() if part.get(u,0) != part.get(v,0))

def count_hyperedge_cuts(hyperedges, part):
    """A hyperedge is cut if its nodes span both partitions."""
    cuts = 0
    for edge in hyperedges:
        blocks = {part.get(q, 0) for q in edge}
        if len(blocks) > 1:
            cuts += 1
    return cuts

def partition_sets(part):
    A = {k for k,v in part.items() if v==0}
    B = {k for k,v in part.items() if v==1}
    return A, B

def get_cut_edges(G, part):
    return [(u,v,G[u][v].get('gate','')) for u,v in G.edges()
            if part.get(u,0) != part.get(v,0)]

# ─────────────────────────────────────────────
# Algorithms
# ─────────────────────────────────────────────

# 1. Brute Force
def algo_brute_force(G, n, hyperedges=None):
    t0 = time.time()
    best_cut, best_part = float('inf'), None
    for subset in combinations(range(n), n//2):
        part = {i:(1 if i in subset else 0) for i in range(n)}
        c = count_cuts(G, part)
        if c < best_cut:
            best_cut, best_part = c, part
    return best_part, best_cut, time.time()-t0

# 2. Spectral
def algo_spectral(G, n, hyperedges=None):
    t0 = time.time()
    L  = nx.laplacian_matrix(G).toarray().astype(float)
    _, vecs = np.linalg.eigh(L)
    fiedler = vecs[:, 1]
    median  = np.median(fiedler)
    part    = {i:(0 if fiedler[i]<=median else 1) for i in range(n)}
    return part, count_cuts(G, part), time.time()-t0

# 3. Kernighan-Lin
def algo_kl(G, n, hyperedges=None):
    t0 = time.time()
    try:
        A_set, B_set = kernighan_lin_bisection(G, seed=42)
        part = {node:(0 if node in A_set else 1) for node in G.nodes()}
    except Exception:
        nodes = list(G.nodes())
        part  = {nodes[i]:(0 if i < len(nodes)//2 else 1) for i in range(len(nodes))}
    return part, count_cuts(G, part), time.time()-t0

# 4. Hypergraph Partitioning (KaHyPar-style, pure Python)
def algo_hypergraph(G, n, hyperedges=None):
    """
    Hypergraph-aware partitioning.
    Minimises the number of cut hyperedges (not just graph edges).
    Uses greedy + local search with hyperedge cost awareness.
    This is the core idea behind KaHyPar / hMETIS.
    """
    t0 = time.time()
    if hyperedges is None or len(hyperedges) == 0:
        # Fallback to spectral if no hyperedges
        part_init = {i:(0 if i < n//2 else 1) for i in range(n)}
    else:
        # ── Step 1: greedy initial partition ──────────────────
        # Pin heavily-connected qubits together using hyperedge weights
        pin_count = {i: 0 for i in range(n)}
        for he in hyperedges:
            for q in he:
                pin_count[q] += 1

        # Sort qubits by pin count descending — most connected first
        sorted_q = sorted(range(n), key=lambda x: -pin_count[x])
        part_init = {}
        for rank, q in enumerate(sorted_q):
            part_init[q] = 0 if rank < n//2 else 1

        # ── Step 2: local search to reduce hyperedge cuts ─────
        best_part = dict(part_init)
        best_cost = count_hyperedge_cuts(hyperedges, best_part)

        T = 2.0   # temperature for acceptance
        for iteration in range(800):
            # Try swapping one node from each partition
            g0 = [k for k,v in best_part.items() if v==0]
            g1 = [k for k,v in best_part.items() if v==1]
            if not g0 or not g1:
                break
            a = random.choice(g0)
            b = random.choice(g1)
            trial = dict(best_part)
            trial[a], trial[b] = 1, 0
            cost = count_hyperedge_cuts(hyperedges, trial)
            delta = cost - best_cost
            # Accept if better, or with small probability if worse
            if delta < 0 or random.random() < np.exp(-delta / max(T, 0.01)):
                best_part = trial
                best_cost = cost
            T *= 0.995   # cooling

    # Final graph cut count (for fair comparison with other algos)
    graph_cuts = count_cuts(G, best_part)
    return best_part, graph_cuts, time.time()-t0

# ─────────────────────────────────────────────
# Circuit helpers
# ─────────────────────────────────────────────
def extract_subcircuit(qc, qubit_group, cut_edges):
    sg   = sorted(qubit_group)
    qmap = {old:new for new,old in enumerate(sg)}
    sub  = QuantumCircuit(len(sg))
    cp   = {(u,v) for u,v,_ in cut_edges} | {(v,u) for u,v,_ in cut_edges}
    for inst in qc.data:
        idxs = [qc.qubits.index(q) for q in inst.qubits]
        if len(idxs)==1 and idxs[0] in qubit_group:
            sub.append(inst.operation, [qmap[idxs[0]]])
        elif len(idxs)==2:
            q0,q1 = idxs
            if q0 in qubit_group and q1 in qubit_group and (q0,q1) not in cp:
                sub.append(inst.operation, [qmap[q0], qmap[q1]])
    return sub

def reconstruct_circuit(qc, cut_edges):
    cp  = {(u,v) for u,v,_ in cut_edges} | {(v,u) for u,v,_ in cut_edges}
    rec = QuantumCircuit(qc.num_qubits)
    for inst in qc.data:
        idxs = [qc.qubits.index(q) for q in inst.qubits]
        if len(idxs)==2 and tuple(idxs) in cp:
            continue
        rec.append(inst.operation, idxs)
    return rec

def noise_analysis(qc, rec_qc, err1, err2):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(err1,1),
                                   ['h','x','y','z','rx','ry','rz'])
    nm.add_all_qubit_quantum_error(depolarizing_error(err2,2), ['cx','cz'])
    sim = AerSimulator(noise_model=nm, method='density_matrix')
    def run(c):
        cc = c.copy(); cc.save_density_matrix()
        return DensityMatrix(sim.run(cc).result().data(0)['density_matrix'])
    f_orig = float(state_fidelity(Statevector.from_instruction(qc),     run(qc)))
    f_rec  = float(state_fidelity(Statevector.from_instruction(rec_qc), run(rec_qc)))
    return f_orig, f_rec

# ─────────────────────────────────────────────
# Graph drawing
# ─────────────────────────────────────────────
def draw_graph(G, partA, partB, cut_edges, title, color_a, color_b="#f59e0b"):
    plt.close('all')
    fig, ax = plt.subplots(figsize=(6,4.5), facecolor='#0a0e1a')
    ax.set_facecolor('#0a0e1a')
    pos = nx.spring_layout(G, seed=42, k=1.8)
    cut_set   = {(u,v) for u,v,_ in cut_edges} | {(v,u) for u,v,_ in cut_edges}
    int_edges = [(u,v) for u,v in G.edges() if (u,v) not in cut_set]
    cut_draw  = [(u,v) for u,v in G.edges() if (u,v) in cut_set]
    nx.draw_networkx_nodes(G, pos, nodelist=list(partA), node_color=color_a, node_size=650, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=list(partB), node_color=color_b, node_size=650, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=int_edges, width=1.8, edge_color='#334155', ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=cut_draw,  width=2.5, edge_color='#ef4444',
                           style='dashed', ax=ax)
    nx.draw_networkx_labels(G, pos, labels={nd:f'q{nd}' for nd in G.nodes()},
                            font_size=9, font_color='white', font_weight='bold', ax=ax)
    pA = mpatches.Patch(color=color_a,   label=f'A: {sorted(partA)}')
    pB = mpatches.Patch(color=color_b,   label=f'B: {sorted(partB)}')
    pC = mpatches.Patch(color='#ef4444', label=f'{len(cut_edges)} cuts')
    ax.legend(handles=[pA,pB,pC], loc='upper left', fontsize=7,
              facecolor='#111827', edgecolor='#1e3a5f', labelcolor='#cbd5e1')
    ax.set_title(title, color='#7ea8c9', fontsize=8, pad=6)
    ax.axis('off')
    plt.tight_layout()
    return fig

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if generate:

    with st.spinner("Generating random circuit..."):
        qc, seed   = generate_random_circuit(min_q, max_q, min_d, max_d)
        n          = qc.num_qubits
        G          = circuit_to_graph(qc)
        hyperedges = circuit_to_hypergraph(qc)

    # Circuit info
    st.markdown('<div class="section-header">Generated Circuit</div>', unsafe_allow_html=True)
    twoq = sum(1 for i in qc.data if len(i.qubits)==2)
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card"><div class="label">Qubits</div><div class="value">{n}</div></div>
      <div class="metric-card"><div class="label">Depth</div><div class="value">{qc.depth()}</div></div>
      <div class="metric-card"><div class="label">Total Gates</div><div class="value">{len(qc.data)}</div></div>
      <div class="metric-card"><div class="label">2-Qubit Gates</div><div class="value">{twoq}</div></div>
      <div class="metric-card"><div class="label">Hyperedges</div><div class="value">{len(hyperedges)}</div></div>
      <div class="metric-card"><div class="label">Seed</div>
        <div class="value" style="font-size:.9rem">{seed}</div></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(" View Circuit Diagram", expanded=False):
        fig_c = qc.draw("mpl", fold=20, scale=0.7,
                        style={'backgroundcolor':'#0a0e1a','textcolor':'#e2e8f0',
                               'gatefacecolor':'#1a56db','gatetextcolor':'white',
                               'linecolor':'#334155'})
        st.pyplot(fig_c); plt.close(fig_c)

    # Algorithm list
    ALGOS = [
        ("Brute Force",   run_bf, algo_brute_force),
        ("Spectral",      run_sp, algo_spectral),
        ("Kernighan-Lin", run_kl, algo_kl),
        ("KaHyPar",    run_hg, algo_hypergraph),
    ]

    if n > 10 and run_bf:
        st.warning(f"⚠️ Brute Force skipped — {n} qubits too large (max 10).")
        ALGOS[0] = ("Brute Force", False, algo_brute_force)

    # Run all algorithms
    st.markdown('<div class="section-header">Partitioning Results</div>', unsafe_allow_html=True)
    results = {}
    active  = [(name, fn) for name, enabled, fn in ALGOS if enabled]
    cols    = st.columns(len(active)) if active else []

    for idx, (name, fn) in enumerate(active):
        col  = cols[idx]
        meta = ALGO_META[name]
        with col:
            with st.spinner(f"Running {name}..."):
                part, cuts, rt = fn(G, n, hyperedges)
            if part is None:
                st.error(f"{name} failed.")
                continue
            partA, partB = partition_sets(part)
            cut_edges    = get_cut_edges(G, part)
            results[name] = dict(part=part, cuts=cuts, rt=rt,
                                 partA=partA, partB=partB, cut_edges=cut_edges)

            st.markdown(f"""
            <div class="algo-card" style="border-color:{meta['color']}">
              <div class="algo-name">{name}</div>
              <div class="algo-cuts" style="color:{meta['color']}">{cuts} cuts</div>
              <div class="algo-time">{rt*1000:.2f} ms &nbsp;|&nbsp; {meta['cat']}</div>
            </div>
            """, unsafe_allow_html=True)

            fig_g = draw_graph(G, partA, partB, cut_edges,
                               f"{name} — {cuts} cuts", meta['color'],  "#f59e0b")
            st.pyplot(fig_g)
            plt.close(fig_g)

    # Comparison table
    if results:
        st.markdown('<div class="section-header">Algorithm Comparison</div>', unsafe_allow_html=True)
        # Step 1: Find minimum cut
        best_cuts = min(r['cuts'] for r in results.values())

        # Step 2: Keep only algorithms with minimum cut
        candidates = {
            name: r
            for name, r in results.items()
            if r['cuts'] == best_cuts
        }

        # Step 3: Among them, choose the one with lowest runtime
        best_algo = min(candidates.items(), key=lambda x: x[1]['rt'])[0]

        rows = ""
        for name, r in results.items():
            meta    = ALGO_META[name]
            is_best = (name == best_algo)
            tag     = '<span class="tag-best">BEST</span>' if is_best else ''
            cat_tag = f'<span class="tag-cat">{meta["cat"]}</span>'
            cls     = 'class="best-row"' if is_best else ''
            rows += f"""
            <tr {cls}>
              <td>{name} {tag} {cat_tag}</td>
              <td>{r['cuts']}</td>
              <td>{r['rt']*1000:.2f} ms</td>
              <td>{sorted(r['partA'])}</td>
              <td>{sorted(r['partB'])}</td>
            </tr>"""

        st.markdown(f"""
        <table class="result-table">
          <thead><tr>
            <th>Algorithm</th><th>Cut Edges</th><th>Runtime</th>
            <th>Group A</th><th>Group B</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>""", unsafe_allow_html=True)

        
        st.markdown(f"""
        <div class="info-box" style="margin-top:1rem">
        Best Overall ({n} qubits):
        <strong style="color:#38b6ff">
        {best_algo}
        </strong>
        </div>
        """, unsafe_allow_html=True)

        # Subcircuits + Noise
        st.markdown(
        '<div class="section-header">Subcircuits · Reconstruction · Noise Analysis</div>',
         unsafe_allow_html=True
        )

        for name, r in results.items():
            meta = ALGO_META[name]

            with st.expander(
                f" {name}  —  {r['cuts']} cuts  |  {r['rt']*1000:.1f} ms",
                expanded=False
            ):
                sub_A = extract_subcircuit(qc, r['partA'], r['cut_edges'])
                sub_B = extract_subcircuit(qc, r['partB'], r['cut_edges'])
                rec   = reconstruct_circuit(qc, r['cut_edges'])

                c1, c2 = st.columns(2)

                with c1:
                    st.markdown(
                        f"**Subcircuit A** — qubits {sorted(r['partA'])}  "
                        f"| {len(sub_A.data)} gates | depth {sub_A.depth()}"
                    )

                    st.write(f"Subcircuit A: {len(sub_A.data)} gates, depth {sub_A.depth()}")

                with c2:
                    st.markdown(
                        f"**Subcircuit B** — qubits {sorted(r['partB'])}  "
                        f"| {len(sub_B.data)} gates | depth {sub_B.depth()}"
                    )

                    st.write(f"Subcircuit B: {len(sub_B.data)} gates, depth {sub_B.depth()}")

                gates_removed = len(qc.data) - len(rec.data)

                twoq_removed = (
                    sum(1 for i in qc.data if len(i.qubits) == 2)
                    -
                    sum(1 for i in rec.data if len(i.qubits) == 2)
                )

                st.markdown(
                    f"**Reconstructed Circuit** — {gates_removed} gates removed "
                    f"({twoq_removed} two-qubit gates cut)"
                )

                figRec = rec.draw("mpl", fold=20)
                st.pyplot(figRec)
                plt.close(figRec)

                ideal_fidelity = float(state_fidelity(
                    Statevector.from_instruction(qc),
                    Statevector.from_instruction(rec)
                ))

                with st.spinner("Running noise simulation..."):
                    f_orig, f_rec = noise_analysis(qc, rec, err1, err2)

                noise_reduced = f_rec > f_orig
                nc = "#38b6ff" if noise_reduced else "#ef4444"
                nl = " Noise Reduced" if noise_reduced else "❌ Noise Increased"

                st.markdown(f"""
                <div class="metric-row">
                  <div class="metric-card">
                    <div class="label">Ideal Fidelity</div>
                    <div class="value" style="font-size:1.4rem">{ideal_fidelity:.4f}</div>
                  </div>
                  <div class="metric-card">
                    <div class="label">Noisy — Original</div>
                    <div class="value" style="font-size:1.4rem;color:#f59e0b">{f_orig:.4f}</div>
                  </div>
                  <div class="metric-card">
                    <div class="label">Noisy — Reconstructed</div>
                    <div class="value" style="font-size:1.4rem;color:{nc}">{f_rec:.4f}</div>
                  </div>
                  <div class="metric-card">
                    <div class="label">Noise Impact</div>
                    <div class="value" style="font-size:1rem;color:{nc}">{nl}</div>
                  </div>
                </div>
                <div class="noise-bar-wrap">
                  <div class="noise-label">Noisy — Original &nbsp; {f_orig:.4f}</div>
                  <div class="noise-bar-bg">
                    <div class="noise-bar-fill" style="width:{f_orig*100:.1f}%;background:#f59e0b"></div>
                  </div>
                </div>
                <div class="noise-bar-wrap">
                  <div class="noise-label">Noisy — Reconstructed &nbsp; {f_rec:.4f}</div>
                  <div class="noise-bar-bg">
                    <div class="noise-bar-fill" style="width:{f_rec*100:.1f}%;background:{nc}"></div>
                  </div>
                </div>
                <div class="info-box" style="margin-top:.8rem">
                  Two-qubit gates removed: {twoq_removed}
                  &nbsp;·&nbsp; Each CX/CZ removed ≈ {err2*100:.1f}% less depolarizing error
                  <br>{' Fewer entangling gates after cut = less accumulated noise.' if noise_reduced else '⚠️ Entanglement loss at cuts outweighed gate reduction benefit.'}
                </div>
                """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem">
      <div style="font-size:4rem;margin-bottom:1.2rem">⚛️</div>
      <div style="font-size:1.1rem;color:#5a7fa0">
        Configure settings in the sidebar and click
        <strong style="color:#38b6ff"> Generate & Run</strong>
      </div>
      <div style="margin-top:1rem;font-size:.82rem;color:#2a3a50;font-family:'JetBrains Mono',monospace">
        Brute Force &nbsp;·&nbsp; Spectral &nbsp;·&nbsp; Kernighan-Lin &nbsp;·&nbsp; Hypergraph
      </div>
    </div>
    """, unsafe_allow_html=True)
