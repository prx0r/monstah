"""Monstah CLI."""

from __future__ import annotations

import argparse
import sys


def _cmd_scenarios(args: argparse.Namespace) -> None:
    from .discovery import ScenarioDiscovery, Taxon
    from .core.models import Reference

    taxa = [
        Taxon(ref=Reference(namespace="pbdb", key="1"), name="Tyrannosaurus rex", min_ma=66.0, max_ma=68.0, env={"land"}, diet="carnivore"),
        Taxon(ref=Reference(namespace="pbdb", key="2"), name="Triceratops", min_ma=66.0, max_ma=68.0, env={"land"}, diet="herbivore"),
        Taxon(ref=Reference(namespace="pbdb", key="3"), name="Mosasaurus", min_ma=66.0, max_ma=72.0, env={"sea"}, diet="carnivore"),
        Taxon(ref=Reference(namespace="pbdb", key="4"), name="Ankylosaurus", min_ma=66.0, max_ma=68.0, env={"land"}, diet="herbivore"),
    ]
    for c in ScenarioDiscovery(taxa).generate(args.top_n):
        print(c)


def _cmd_ingest(args: argparse.Namespace) -> None:
    from .domains import PaleoLoader

    loader = PaleoLoader(cache_dir=args.cache)
    names = args.taxa or ["Tyrannosaurus rex", "Mosasaurus"]
    for name in names:
        ent = loader.load_taxon(name)
        print(f"{ent.name:24} pbdb={ent.refs[0].key} traits={ent.traits}")


def _cmd_run(args: argparse.Namespace) -> None:
    from .discovery import ScenarioDiscovery, Taxon
    from .core.models import Reference
    from .pipeline import run_candidate, save_to_r2

    taxa = [
        Taxon(ref=Reference(namespace="pbdb", key="1"), name="Tyrannosaurus rex", min_ma=66.0, max_ma=68.0, env={"land"}, diet="carnivore", traits={"mass_kg": 7000, "speed": 10, "bite_force": 40000, "stamina": 12}),
        Taxon(ref=Reference(namespace="pbdb", key="2"), name="Triceratops", min_ma=66.0, max_ma=68.0, env={"land"}, diet="herbivore", traits={"mass_kg": 6000, "speed": 9, "defence": 0.6}),
        Taxon(ref=Reference(namespace="pbdb", key="3"), name="Mosasaurus", min_ma=66.0, max_ma=72.0, env={"sea"}, diet="carnivore", traits={"mass_kg": 12000, "speed": 12, "bite_force": 60000}),
        Taxon(ref=Reference(namespace="pbdb", key="4"), name="Ankylosaurus", min_ma=66.0, max_ma=68.0, env={"land"}, diet="herbivore", traits={"mass_kg": 5000, "defence": 0.85}),
        Taxon(ref=Reference(namespace="pbdb", key="5"), name="Velociraptor", min_ma=70.0, max_ma=75.0, env={"land"}, diet="carnivore", traits={"mass_kg": 15, "speed": 14, "bite_force": 500}),
    ]
    by_ref = {t.ref.key: t for t in taxa}
    cands = ScenarioDiscovery(taxa).generate(args.top_n)
    for cand in cands:
        out = run_candidate(cand, by_ref, n_runs=args.n_runs)
        print(f"\n=== {out.story.title} ===")
        print(f"  overlap: {out.overlap.summary()}  valid={out.overlap.valid_historical}")
        print(f"  outcomes: {out.mc.outcomes}")
        print(f"  significance: {out.significance.score} {out.significance.signals}")
        if args.r2:
            key = save_to_r2(out)
            print(f"  stored -> r2:{key}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="monstah", description="world model engine")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scenarios", help="run scenario discovery on a corpus")
    s.add_argument("--top-n", type=int, default=10, dest="top_n")
    s.set_defaults(func=_cmd_scenarios)

    i = sub.add_parser("ingest", help="ingest taxa from PBDB + Macrostrat")
    i.add_argument("taxa", nargs="*")
    i.add_argument("--cache", default="~/.cache/monstah")
    i.set_defaults(func=_cmd_ingest)

    r = sub.add_parser("run", help="run the full pipeline over discovered scenarios")
    r.add_argument("--top-n", type=int, default=5, dest="top_n")
    r.add_argument("--runs", type=int, default=500, dest="n_runs")
    r.add_argument("--r2", action="store_true", help="store bundles to R2")
    r.set_defaults(func=_cmd_run)

    args = p.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
