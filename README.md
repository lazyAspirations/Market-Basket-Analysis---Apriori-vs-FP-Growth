
# Market Basket Analysis: Apriori vs. FP-Growth

This project, conducted by **Aissat Mohamed Moncef** for the **Data Mining** course (Academic Year 2025-2026), implements and compares two major association rule mining algorithms: **Apriori** and **FP-Growth**[cite: 1].

## 📋 Project Objective
The goal of this assignment is to discover frequent co-occurrences between items in a transaction database. The performance and results are measured using **Support** (itemset frequency) and **Confidence** (the probability of a consequent appearing given the antecedent).

## 📊 Dataset Description
* **File**: `Market Basket Optimisation.csv`.
* **Volume**: 7,501 transactions.
* **Content**: Each line represents a shopping basket with items such as 'mineral water', 'eggs', 'spaghetti', and 'chocolate'.
* **Preprocessing**: Transactions were read line-by-line, stripped of whitespace, and converted into `frozensets` to facilitate set operations.

## ⚙️ Algorithms Implemented
### 1. Apriori
This algorithm relies on the **anti-monotone property**, stating that any subset of a frequent itemset must also be frequent. It works through:
* **Candidate Generation**: Joining frequent itemsets from previous levels.
* **Pruning**: Removing candidates whose subsets are not frequent.
* **Support Counting**: Scanning the database to count occurrences.

### 2. FP-Growth (Frequent Pattern Growth)
FP-Growth improves upon Apriori by avoiding explicit candidate generation and only scanning the database twice.
* **FP-Tree Construction**: Building a compact tree structure to represent the database.
* **Recursive Extraction**: Extracting frequent patterns through conditional pattern bases and conditional trees.

## 🚀 Results & Comparison
Both algorithms were tested using a **Minimum Support of 0.005** and a **Minimum Confidence of 0.5**.

| Metric | Apriori | FP-Growth |
| :--- | :--- | :--- |
| **Execution Time** | 4.2373 seconds | 0.1596 seconds |
| **Frequent Itemsets** | 725 | 725 |
| **Association Rules** | 20 | 20 |

**Key Finding**: FP-Growth is approximately **26.55x faster** than Apriori because it avoids the overhead of candidate generation.

## 🔍 Top Rule Analysis
* **Dominant Item**: 'Mineral water' is a central product, appearing in 9 out of the top 10 rules.
* **Highest Confidence**: The rule `{frozen vegetables, soup} -> {mineral water}` achieved the highest confidence at **0.6333**.
* **Complexity**: Rules with two items in the antecedent generally show higher confidence than those with a single item.

## 🛠️ Future Improvements
* **Advanced Metrics**: Integrate **Lift**, **Conviction**, and **Leverage** to filter redundant rules.
* **Visualization**: Implement dependency graphs or scatter plots to better interpret rule relationships.
* **Optimized Libraries**: Use specialized libraries like `mlxtend` or `pyfpgrowth` for even larger datasets.

