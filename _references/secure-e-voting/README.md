# vSPACE FormalBench EF-DA-TASK Kaggle Benchmark Suite

## Overview

This directory contains the vSPACE FormalBench EF-DA-TASK benchmark suite for evaluating Lean 4 proof generation against **Executive Functions (EF)** cognitive abilities, specifically the **Directing Action (DA)** sub-abilities as defined in the DeepMind AGI cognitive framework (§7.8).

The benchmark suite measures **seven distinct EF assertions** derived from the DeepMind *Measuring Progress Toward AGI: A Cognitive Framework* (Burnell et al., 2026) across 1,239 formally verified Lean 4 proof tasks spanning cryptographic protocols, election systems, and zero-knowledge proofs.

## Files

| Notebook | EF-DA Subability | Task Focus | Difficulty Categories | Tasks |
|----------|-----------------|------------|---------------------|-------|
| `00_FormalBench_EF_DA_TASK_Unified.ipynb` | **Both** | Complete framework | All 6 | 1,239 |
| `01_Planning_MultiStep_Proofs.ipynb` | Planning (§7.8.1) | Multi-step proof construction | All | 1,239 |
| `02_Goal_Setting_Theorem_Statements.ipynb` | Goal Setting (§7.8.2) | Theorem formulation | All | 1,239 |
| `03_Planning_Cryptographic_Proofs.ipynb` | Planning (§7.8.1) | Cryptographic verification | coq_based, basic_core | 500 |
| `04_Goal_Setting_Proof_Strategies.ipynb` | Goal Setting (§7.8.2) | Strategy selection | autonomous, augmented | 550 |
| `05_Planning_Decision_Tree_Search.ipynb` | Planning (§7.8.1) | Tactic decision trees | advanced, autonomous | 381 |
| `06_Goal_Setting_Working_Memory.ipynb` | Goal Setting (§7.8.2) | Proof state management | All | 1,239 |

## Cognitive Framework

### Executive Functions (EF) Track

Based on: **Measuring Progress Toward AGI: A Cognitive Framework** (DeepMind, 2026)

**Reference**: https://www.kaggle.com/competitions/kaggle-measuring-agi

#### §7.8 Executive Functions

Higher-order cognitive abilities that enable goal-directed behavior by regulating and orchestrating thoughts and actions (Diamond, 2013).

#### Seven EF Assertions ↔ §7.8.x Sub-Abilities

The benchmark evaluates Lean 4 proof generation against seven specific assertions, each mapped to a cognitive sub-ability:

| # | Ref | Sub-Ability | Lean 4 Operationalization |
|---|-----|-------------|---------------------------|
| 1 | 7.8.1 | **Goal Setting & Maintenance** | Proof preserves theorem/lemma goal statement |
| 2 | 7.8.2 | **Planning** | Multi-step tactic sequence (>=2 distinct tactics) |
| 3 | 7.8.3 | **Inhibitory Control** | Suppresses `sorry`/`admit` shortcuts |
| 4 | 7.8.4 | **Cognitive Flexibility** | Uses tactics from >=2 distinct categories |
| 5 | 7.8.5 | **Conflict Resolution** | Manages competing subgoals (case splits, focused goals) |
| 6 | 7.8.6 | **Working Memory** | Tracks intermediate state (`have`/`let`/`obtain`/`suffices`) |
| 7 | 7.8   | **Composite EF Integration** | Overall structural validity (proof body + balanced syntax) |

### Dataset: v_train_extended.csv

**Source**: Generated from vSPACE proof task generator

**Statistics**:
- **Total proof tasks**: 1,239
- **File size**: 2.79 MB
- **Lines**: 68,647 (with multiline Lean4 code)

**Difficulty Distribution**:
| Category | Count | Description |
|----------|-------|-------------|
| `basic` | 108 | Original Verina basic programming |
| `advanced` | 81 | Original Verina advanced programming |
| `coq_based` | 250 | Converted from Coq/ElectionGuard proofs |
| `basic_core` | 250 | F-001 to F-012 (ElectionGuard Core2) |
| `autonomous` | 300 | F-100 to F-103, F-109, F-110 (vSPACE) |
| `augmented` | 250 | F-104 to F-108 (Azure/Entra) |

**Features**:
- Formal verification of cryptographic protocols
- Election system correctness proofs
- Zero-knowledge proof verification
- Modular arithmetic, ElGamal encryption, BBS signatures
- SAAC protocol, credential binding, one-show enforcement

## Kaggle Benchmarks SDK Implementation

### Task Definition Pattern

The benchmark implements the `@kbench.task` decorator pattern returning a `tuple[int, int]` representing `(passed_assertions, total_assertions)`:

```python
import kaggle_benchmarks as kbench

@kbench.task(name="agi_ef_tasks", store_task=True)
def agi_ef_tasks(llm) -> tuple[int, int]:
    """
    EF-DA-TASK: Measures Executive Functions in Lean 4 proof generation.
    
    Evaluates 7 EF assertions across all 1,239 vSPACE Lean 4 proof tasks.
    
    Returns:
        tuple[int, int]: (passed_assertions, total_assertions) where
                         total_assertions = num_rows x 7 = 8,673
    """
    # Implementation extracts Lean 4 proofs from LLM responses
    # and evaluates against 7 EF assertion functions
    # Returns aggregated counts for leaderboard scoring
```

### Evaluation Pipeline

```python
# Load dataset
df = pd.read_csv('v_train_extended.csv')

# Run benchmark (returns tuple[int, int] for leaderboard)
results = agi_ef_tasks.evaluate(
    stop_condition=lambda runs: len(runs) == len(df),
    llm=[llm],
    evaluation_data=df,
    n_jobs=4,
    timeout=300
)

# Results are automatically formatted for Kaggle leaderboard
# as a Numerical_Result displaying passed/total ratio
```

## Detailed Metrics

### EF Assertion Functions

Each assertion returns a boolean indicating whether the generated proof satisfies the corresponding cognitive sub-ability:

1. **7.8.1 Goal Setting & Maintenance**: Preserves theorem goal via `theorem`/`lemma` keyword
2. **7.8.2 Planning**: Multi-step sequencing via >=2 distinct tactics
3. **7.8.3 Inhibitory Control**: No `sorry`/`admit` in proof body
4. **7.8.4 Cognitive Flexibility**: >=2 tactic categories used
5. **7.8.5 Conflict Resolution**: Subgoal management via `case`/`have`/`next`
6. **7.8.6 Working Memory**: Intermediate state via `have`/`let`/`obtain`/`suffices`
7. **7.8 Composite EF Integration**: Structural validity (proof body + balanced syntax)

### Per-Assertion Breakdown

The benchmark provides detailed per-assertion statistics:
- Raw counts of passed/failed assertions per category
- Percentage success rates
- Visual progress tracking during execution
- Per-difficulty breakdowns
- Perfect score tracking (7/7 assertions passed)

## Usage

### Running Individual Notebooks

```bash
cd _references/secure-e-voting

# Run unified benchmark (all 7 EF assertions)
jupyter execute 00_FormalBench_EF_DA_TASK_Unified.ipynb

# Run specific EF sub-ability notebook
jupyter execute 01_Planning_MultiStep_Proofs.ipynb
```

### Kaggle Submission Process

1. **Create Kaggle Notebook**: Copy benchmark code to Kaggle kernel
2. **Upload Dataset**: Upload `v_train_extended.csv` to Kaggle dataset
3. **Configure LLM**: Select appropriate language model (Gemini, GPT, etc.)
4. **Run Evaluation**: Execute all cells to generate `tuple[int, int]` result
5. **Submit Results**: Submit to "Measuring AGI" competition as Numerical_Result

### Expected Runtime

| Notebook | Tasks | Est. Time (4 jobs) | Est. Time (8 jobs) |
|----------|-------|-------------------|-------------------|
| 00_Unified | 1,239 | ~60 min | ~30 min |
| 01_Planning_MultiStep | 1,239 | ~60 min | ~30 min |
| 02_Goal_Setting_Theorem | 1,239 | ~40 min | ~20 min |
| 03_Planning_Crypto | 500 | ~25 min | ~13 min |
| 04_Goal_Setting_Strategy | 550 | ~28 min | ~14 min |
| 05_Planning_Decision_Tree | 381 | ~20 min | ~10 min |
| 06_Goal_Setting_Working_Memory | 1,239 | ~60 min | ~30 min |

**Note**: Times assume 2048 tokens max, 0.2 temperature, 2s per task average.

## Output Files

After execution, each notebook generates:

1. **Results CSV**: `results_{notebook_name}.csv` - Detailed per-task results
2. **Analysis JSON**: `analysis_{notebook_name}.json` - Aggregated metrics
3. **Visualization PNG**: `ef_da_task_results.png` - EF assertion performance charts
4. **Log File**: `benchmark_{timestamp}.log` - Execution progress and timing

## Directory Structure

```
_references/secure-e-voting/
├── v_train.csv                    # Original Verina dataset (189 tasks)
├── v_train_extended.csv           # Extended dataset (1,239 tasks)
├── generate_vspace_proofs.py      # Proof task generator (v1.0)
├── PROOF_TASKS.md                 # Proof task categories documentation
├── 00_FormalBench_EF_DA_TASK_Unified.ipynb  # Unified EF-DA-TASK benchmark
├── 01_Planning_MultiStep_Proofs.ipynb       # Planning-focused benchmark
├── 02_Goal_Setting_Theorem_Statements.ipynb # Goal Setting-focused benchmark
├── 03_Planning_Cryptographic_Proofs.ipynb   # Crypto-focused Planning benchmark
├── 04_Goal_Setting_Proof_Strategies.ipynb   # Goal Setting Strategy benchmark
├── 05_Planning_Decision_Tree_Search.ipynb   # Decision Tree Planning benchmark
├── 06_Goal_Setting_Working_Memory.ipynb     # Working Memory Goal Setting benchmark
└── README.md                      # This file
```

## References

### Academic

- Burnell, R. et al. (2026). Measuring Progress Toward AGI: A Cognitive Framework. Google DeepMind.
- Diamond, A. (2013). Executive functions. *Annual Review of Psychology*, 64, 135-168.
- Owen, A. M. (1997). Cognitive planning in humans: Neuropsychological, neuroanatomical and neuropharmacological perspectives. *Progress in Neurobiology*, 52(6), 433-450.
- Buschman, T. J., & Miller, E. K. (2014). Goal-direction and top-down control. *Philosophical Transactions of the Royal Society B*, 369(1655), 20130471.
- Dickinson, A., & Balleine, B. (1994). Motivational control of goal-directed action. *Animal Learning & Behavior*, 22(1), 1-18.
- Mattar, M. G., & Lengyel, M. (2022). Planning as inference in a hierarchical model. *Nature Neuroscience*, 25, 1197-1208.

### Technical

- Kaggle Benchmarks SDK Cookbook: https://github.com/Kaggle/kaggle-benchmarks/blob/ci/cookbook.md
- Lean 4 Documentation: https://leanprover.github.io/
- Mathlib4: https://github.com/leanprover-community/mathlib4
- vSPACE Repository: https://github.com/vSpaceVote/vSPACE
- ElectionGuard Coq Proofs: https://github.com/gerlion/secure-e-voting-with-coq/tree/master/ElectionGuard

## License

MIT License (aligned with vSPACE and ElectionGuard ecosystem)

---
*Generated: 2026-04-16*  
*Version: 1.0.0*  
*Contact: vSPACE Research Team*