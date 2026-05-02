"""
Association Rule Mining: Apriori vs FP-Growth (Corrected)
Author: Student
Date: 2026-05-01
Description: Robust implementations of Apriori and FP-Growth.
"""

import time
from collections import defaultdict, Counter
from itertools import combinations

# ------------------------------------------------------------
# 1. Data loading
# ------------------------------------------------------------
def load_transactions(filepath):
    transactions = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                items = [item.strip() for item in line.split(',') if item.strip()]
                if items:
                    transactions.append(frozenset(items))
    return transactions

# ------------------------------------------------------------
# 2. Apriori (unchanged, works correctly)
# ------------------------------------------------------------
class Apriori:
    def __init__(self, transactions, min_support=0.005, min_confidence=0.5):
        self.transactions = transactions
        self.num_transactions = len(transactions)
        self.min_support = min_support
        self.min_support_count = min_support * self.num_transactions
        self.min_confidence = min_confidence
        self.freq_itemsets = {}
        self.rules = []

    def _get_frequent_itemsets(self):
        item_counts = Counter()
        for trans in self.transactions:
            item_counts.update(trans)
        L1 = {frozenset([item]): count for item, count in item_counts.items()
              if count >= self.min_support_count}
        self.freq_itemsets.update(L1)
        k = 2
        prev_itemsets = list(L1.keys())
        while prev_itemsets:
            candidates = self._apriori_gen(prev_itemsets, k)
            if not candidates:
                break
            candidate_counts = defaultdict(int)
            for trans in self.transactions:
                for cand in candidates:
                    if cand.issubset(trans):
                        candidate_counts[cand] += 1
            new_freq = {cand: count for cand, count in candidate_counts.items()
                        if count >= self.min_support_count}
            if not new_freq:
                break
            self.freq_itemsets.update(new_freq)
            prev_itemsets = list(new_freq.keys())
            k += 1

    def _apriori_gen(self, freq_itemsets, k):
        candidates = []
        n = len(freq_itemsets)
        itemsets_list = list(freq_itemsets)
        for i in range(n):
            for j in range(i+1, n):
                list_i = sorted(itemsets_list[i])
                list_j = sorted(itemsets_list[j])
                if list_i[:k-2] == list_j[:k-2]:
                    new_cand = frozenset(list_i) | frozenset(list_j)
                    # Prune
                    if all(frozenset(subset) in self.freq_itemsets
                           for subset in combinations(new_cand, k-1)):
                        candidates.append(new_cand)
        return candidates

    def _generate_rules(self):
        for itemset, supp_count in self.freq_itemsets.items():
            if len(itemset) < 2:
                continue
            for i in range(1, len(itemset)):
                for ante in combinations(itemset, i):
                    ante_set = frozenset(ante)
                    cons_set = itemset - ante_set
                    supp_ante = self.freq_itemsets[ante_set]
                    confidence = supp_count / supp_ante
                    if confidence >= self.min_confidence:
                        support = supp_count / self.num_transactions
                        self.rules.append((ante_set, cons_set, support, confidence))

    def run(self):
        start = time.time()
        self._get_frequent_itemsets()
        self._generate_rules()
        elapsed = time.time() - start
        return self.freq_itemsets, self.rules, elapsed

# ------------------------------------------------------------
# 3. FP-Growth (corrected)
# ------------------------------------------------------------
class FPNode:
    __slots__ = ('item', 'count', 'parent', 'children', 'node_link')
    def __init__(self, item, parent):
        self.item = item
        self.count = 1
        self.parent = parent
        self.children = {}
        self.node_link = None

class FPTree:
    def __init__(self):
        self.root = FPNode(None, None)
        self.header_table = defaultdict(list)

class FPGrowth:
    def __init__(self, transactions, min_support=0.005, min_confidence=0.5):
        self.transactions = transactions
        self.num_transactions = len(transactions)
        self.min_support = min_support
        self.min_support_count = min_support * self.num_transactions
        self.min_confidence = min_confidence
        self.freq_itemsets = {}
        self.rules = []

    def _build_tree(self, transactions):
        """Build FP-tree; returns (tree, item_counts) or (None, None) if no frequent items."""
        # Count frequencies
        item_counts = Counter()
        for trans in transactions:
            item_counts.update(trans)
        frequent_items = {item for item, cnt in item_counts.items()
                          if cnt >= self.min_support_count}
        if not frequent_items:
            return None, None

        # Sort each transaction by descending frequency
        ordered_trans = []
        for trans in transactions:
            ordered = [item for item in trans if item in frequent_items]
            ordered.sort(key=lambda x: item_counts[x], reverse=True)
            if ordered:
                ordered_trans.append(ordered)
        if not ordered_trans:
            return None, None

        tree = FPTree()
        for trans in ordered_trans:
            current = tree.root
            for item in trans:
                if item in current.children:
                    child = current.children[item]
                    child.count += 1
                else:
                    child = FPNode(item, current)
                    current.children[item] = child
                    tree.header_table[item].append(child)
                current = child
        return tree, item_counts

    def _mine_tree(self, tree, item_counts, prefix, freq_itemsets):
        """Recursive mining of FP-tree."""
        # Process items in increasing order of frequency
        items = sorted(tree.header_table.keys(), key=lambda x: item_counts[x])
        for item in items:
            new_prefix = prefix + [item]
            new_itemset = frozenset(new_prefix)
            # Support = sum of counts of nodes for this item in header table
            support = sum(node.count for node in tree.header_table[item])
            if support >= self.min_support_count:
                freq_itemsets[new_itemset] = support
                # Build conditional pattern base
                cond_patterns = []
                for node in tree.header_table[item]:
                    path = []
                    curr = node.parent
                    while curr.item is not None:
                        path.append(curr.item)
                        curr = curr.parent
                    if path:
                        cond_patterns.extend([path] * node.count)
                if cond_patterns:
                    cond_tree, cond_counts = self._build_tree(cond_patterns)
                    if cond_tree is not None:
                        self._mine_tree(cond_tree, cond_counts, new_prefix, freq_itemsets)

    def _generate_rules(self):
        for itemset, supp_count in self.freq_itemsets.items():
            if len(itemset) < 2:
                continue
            for i in range(1, len(itemset)):
                for ante in combinations(itemset, i):
                    ante_set = frozenset(ante)
                    cons_set = itemset - ante_set
                    if ante_set in self.freq_itemsets:
                        confidence = supp_count / self.freq_itemsets[ante_set]
                        if confidence >= self.min_confidence:
                            support = supp_count / self.num_transactions
                            self.rules.append((ante_set, cons_set, support, confidence))

    def run(self):
        start = time.time()
        tree, item_counts = self._build_tree(self.transactions)
        if tree is not None:
            self._mine_tree(tree, item_counts, [], self.freq_itemsets)
        self._generate_rules()
        elapsed = time.time() - start
        return self.freq_itemsets, self.rules, elapsed

# ------------------------------------------------------------
# 4. Main
# ------------------------------------------------------------
def print_results(algorithm_name, freq_itemsets, rules, elapsed_time, min_support, min_confidence):
    print(f"\n{'='*60}")
    print(f"Algorithm: {algorithm_name}")
    print(f"Parameters: min_support = {min_support}, min_confidence = {min_confidence}")
    print(f"Number of frequent itemsets: {len(freq_itemsets)}")
    print(f"Number of association rules: {len(rules)}")
    print(f"Execution time: {elapsed_time:.4f} seconds")
    if rules:
        print("\nTop 10 rules (by confidence):")
        top_rules = sorted(rules, key=lambda x: x[3], reverse=True)[:10]
        for i, (ant, cons, supp, conf) in enumerate(top_rules, 1):
            ant_str = ', '.join(sorted(ant))
            cons_str = ', '.join(sorted(cons))
            print(f"{i}. {ant_str} -> {cons_str}  (support={supp:.4f}, confidence={conf:.4f})")
    print(f"{'='*60}")

def main():
    filepath = "Market_Basket_Optimisation.csv"
    print("Loading transactions...")
    transactions = load_transactions(filepath)
    print(f"Loaded {len(transactions)} transactions.\n")

    min_support = 0.005
    min_confidence = 0.5

    # Apriori
    apriori = Apriori(transactions, min_support, min_confidence)
    ap_freq, ap_rules, ap_time = apriori.run()
    print_results("Apriori", ap_freq, ap_rules, ap_time, min_support, min_confidence)

    # FP-Growth
    fpg = FPGrowth(transactions, min_support, min_confidence)
    fp_freq, fp_rules, fp_time = fpg.run()
    print_results("FP-Growth", fp_freq, fp_rules, fp_time, min_support, min_confidence)

    # Comparison
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"Apriori      : {ap_time:.4f} sec, {len(ap_freq)} itemsets, {len(ap_rules)} rules")
    print(f"FP-Growth    : {fp_time:.4f} sec, {len(fp_freq)} itemsets, {len(fp_rules)} rules")
    speedup = ap_time / fp_time if fp_time > 0 else float('inf')
    print(f"Speed-up (Apriori/FP-Growth): {speedup:.2f}x")
    print("Note: FP-Growth is generally faster because it avoids candidate generation.")

if __name__ == "__main__":
    main()