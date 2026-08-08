"""
Ablation Statistics: Friedman + Wilcoxon
==========================================

This is what actually closes Reviewer 1's gate (research/REVISION_PLAN_incit2026.md,
Phase 4, item 3). Reads eval_summary.json for every (variant, seed) produced
by training/evaluate_variant.py, builds a seeds x variants matrix of a
chosen performance metric, then runs:

    - Friedman test across all variants (are the methods different at all?)
    - Wilcoxon signed-rank, d3qn_full vs every other variant (pairwise,
      is the full method significantly different from each ablation/baseline?)
    - Coefficient of variation per variant across seeds (stability --
      lower CV = more consistent training, independent of significance)

Requires all 6 variants to have the SAME set of seeds evaluated, since both
tests are paired-by-seed. If a seed is missing for any variant, that seed's
row is dropped from the matrix (and reported) rather than silently padded.

Usage:
    python training/stats_ablation.py                          # metric=mean_reward, all seeds found
    python training/stats_ablation.py --metric mean_vulns
    python training/stats_ablation.py --metric overall_detection_rate

Output:
    research/results/ablation_stats.json  -- full results, ready to drop into the paper
    (also printed to terminal as a readable table)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import glob
import json
import statistics

VARIANTS = ["random", "dqn", "d3qn_full", "d3qn_no_per", "d3qn_no_noisy", "d3qn_no_multistep"]
LOG_ROOT = "logs/ablation"
OUT_PATH = "research/results/ablation_stats.json"


def load_all_summaries():
    """variant -> {seed: summary_dict}"""
    data = {v: {} for v in VARIANTS}
    for path in glob.glob(f"{LOG_ROOT}/*/eval_summary.json"):
        with open(path, encoding="utf-8") as f:
            s = json.load(f)
        v, seed = s["variant"], s["seed"]
        if v in data:
            data[v][seed] = s
    return data


def build_matrix(data, metric):
    """Returns (seeds_used, {variant: [values in seed order]}), dropping any
    seed not present for all variants."""
    seed_sets = [set(data[v].keys()) for v in VARIANTS if data[v]]
    if not seed_sets:
        return [], {}
    common_seeds = sorted(set.intersection(*seed_sets)) if len(seed_sets) == len(VARIANTS) else []
    matrix = {}
    for v in VARIANTS:
        matrix[v] = [data[v][s][metric] for s in common_seeds] if common_seeds else []
    return common_seeds, matrix


def coefficient_of_variation(values):
    if len(values) < 2:
        return None
    mean = statistics.mean(values)
    if mean == 0:
        return None
    return statistics.stdev(values) / abs(mean)


def run(metric="mean_reward"):
    data = load_all_summaries()

    print("=" * 70)
    print(f"ABLATION STATISTICS -- metric: {metric}")
    print("=" * 70)
    for v in VARIANTS:
        seeds_found = sorted(data[v].keys())
        print(f"  {v:<20s} seeds evaluated: {seeds_found if seeds_found else '(none yet)'}")

    common_seeds, matrix = build_matrix(data, metric)
    result = {
        "metric": metric,
        "seeds_available_per_variant": {v: sorted(data[v].keys()) for v in VARIANTS},
        "common_seeds_used": common_seeds,
    }

    if not common_seeds:
        print("\n⚠️  No seed is present across ALL 6 variants yet -- can't run paired "
              "Friedman/Wilcoxon. Run training/evaluate_variant.py for the missing "
              "combinations first (see per-variant seed lists above).")
        result["status"] = "insufficient_data"
        _write(result)
        return result

    print(f"\nUsing {len(common_seeds)} common seed(s): {common_seeds}")
    if len(common_seeds) < 3:
        print("⚠️  Fewer than 3 seeds -- Friedman/Wilcoxon will run but are statistically "
              "weak with this few samples. Reviewer 1 may push back; disclose this "
              "honestly in the paper if you can't get to 3+.")

    # Per-variant descriptive stats (mean, stdev, CV) -- these are meaningful
    # even with too few seeds for a real significance test.
    per_variant_stats = {}
    for v in VARIANTS:
        vals = matrix[v]
        per_variant_stats[v] = {
            "n": len(vals),
            "mean": statistics.mean(vals) if vals else None,
            "stdev": statistics.stdev(vals) if len(vals) > 1 else None,
            "coefficient_of_variation": coefficient_of_variation(vals),
            "values": vals,
        }
    result["per_variant_stats"] = per_variant_stats

    print("\nPer-variant (mean ± stdev, CV = stability, lower is more consistent):")
    for v in VARIANTS:
        s = per_variant_stats[v]
        if s["mean"] is None:
            print(f"  {v:<20s} no data")
            continue
        cv_str = f"{s['coefficient_of_variation']:.3f}" if s["coefficient_of_variation"] is not None else "n/a"
        stdev_str = f"{s['stdev']:.3f}" if s["stdev"] is not None else "n/a"
        print(f"  {v:<20s} mean={s['mean']:.3f}  stdev={stdev_str}  CV={cv_str}")

    # Friedman test (needs >=3 variants with data, run across all 6 if all present)
    try:
        from scipy import stats as scipy_stats
    except ImportError:
        print("\n⚠️  scipy not installed -- run `pip install scipy` to get the actual "
              "Friedman/Wilcoxon numbers. Descriptive stats above still saved.")
        result["status"] = "scipy_missing"
        _write(result)
        return result

    active_variants = [v for v in VARIANTS if len(matrix[v]) == len(common_seeds) and len(common_seeds) >= 3]
    if len(active_variants) >= 3:
        samples = [matrix[v] for v in active_variants]
        stat, p = scipy_stats.friedmanchisquare(*samples)
        result["friedman"] = {"variants": active_variants, "statistic": stat, "p_value": p}
        print(f"\nFriedman test across {active_variants}: statistic={stat:.4f}, p={p:.4g}")
        print("  (p < 0.05 => the methods are not all equivalent)")
    else:
        print("\n⚠️  Fewer than 3 seeds or variants with full data -- skipping Friedman test.")
        result["friedman"] = None

    # Pairwise Wilcoxon signed-rank: d3qn_full vs every other variant.
    wilcoxon_results = {}
    full_vals = matrix.get("d3qn_full", [])
    if full_vals and len(common_seeds) >= 3:
        for v in VARIANTS:
            if v == "d3qn_full" or not matrix[v]:
                continue
            try:
                stat, p = scipy_stats.wilcoxon(full_vals, matrix[v])
                wilcoxon_results[v] = {"statistic": stat, "p_value": p}
                print(f"Wilcoxon d3qn_full vs {v}: statistic={stat:.4f}, p={p:.4g}")
            except ValueError as e:
                wilcoxon_results[v] = {"error": str(e)}
                print(f"Wilcoxon d3qn_full vs {v}: could not compute ({e})")
    else:
        print("\n⚠️  Skipping Wilcoxon pairwise tests (need d3qn_full data + >=3 seeds).")
    result["wilcoxon_vs_d3qn_full"] = wilcoxon_results

    result["status"] = "ok"
    _write(result)
    print(f"\n✅ Saved to {OUT_PATH}")
    return result


def _write(result):
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metric", default="mean_reward",
        choices=["mean_reward", "mean_vulns", "overall_detection_rate"],
    )
    args = parser.parse_args()
    run(metric=args.metric)
