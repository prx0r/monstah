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

    def mk(key, name, region, diet, **gp):
        t = Taxon(
            ref=Reference(namespace="pbdb", key=key),
            name=name, min_ma=66.0, max_ma=68.0, env={"land"}, diet=diet, region=region,
        )
        t.set_evidence("mass_kg", gp.pop("mass_kg", 2000), unit="kg")
        for k, v in gp.items():
            t.set_game_proxy(k, v, source="demo")
        return t

    taxa = [
        mk("1", "Tyrannosaurus rex", "Hell Creek", "carnivore", mass_kg=7000, armor_class=13, hit_points=70, attack_bonus=11, damage_dice="4d12+7", speed=10),
        mk("2", "Triceratops", "Hell Creek", "herbivore", mass_kg=6000, armor_class=15, hit_points=85, attack_bonus=9, damage_dice="3d8+6", speed=9),
        mk("3", "Mosasaurus", "Western Interior Seaway", "carnivore", mass_kg=12000, armor_class=14, hit_points=100, attack_bonus=12, damage_dice="4d10+8", speed=12),
        mk("4", "Ankylosaurus", "Hell Creek", "herbivore", mass_kg=5000, armor_class=19, hit_points=90, attack_bonus=8, damage_dice="3d10+6", speed=8),
    ]
    by_ref = {t.ref.key: t for t in taxa}
    cands = ScenarioDiscovery(taxa).generate(args.top_n)
    for cand in cands:
        out = run_candidate(cand, by_ref, n_runs=args.n_runs)
        print(f"\n=== {out.story.title} ===")
        print(f"  overlap: {out.overlap.summary()}  valid={out.overlap.valid_historical}")
        print(f"  outcomes: {out.mc.outcomes}")
        print(f"  selected runs: {out.mc.selected}")
        print(f"  significance: {out.significance.score} {out.significance.signals}")
        if args.r2:
            key = save_to_r2(out)
            print(f"  stored -> r2:{key}")


def _cmd_matchup(args: argparse.Namespace) -> int:
    from .ingest.open5e import Open5eClient
    from .simulations import Combatant, run_monte_carlo

    c = Open5eClient(cache_dir=args.cache)
    stats_a = c.monster(args.a)
    stats_b = c.monster(args.b)
    if not stats_a or not stats_b:
        print("could not resolve both monster slugs")
        return 1
    a = Combatant.from_open5e(stats_a)
    b = Combatant.from_open5e(stats_b)
    mc = run_monte_carlo(a, b, n=args.runs)
    print(f"{a.name} (AC {a.armor_class}, HP {a.hit_points}, {a.damage_dice})")
    print(f"  vs")
    print(f"{b.name} (AC {b.armor_class}, HP {b.hit_points}, {b.damage_dice})")
    print(f"\n  outcomes (n={mc.runs}): {mc.outcomes}")
    print(f"  selected runs: {mc.selected}")
    return 0


def _cmd_channel(args: argparse.Namespace) -> int:
    from .channels import get_channel, list_channels

    ch = get_channel(args.channel, n_runs=args.runs)
    print(f"## Channel: {ch.theme} — {ch.manifest.title}\n")
    taxa = ch.ingest(limit=args.taxa)
    by_ref = {t.ref.key: t for t in taxa}
    print(f"ingested {len(taxa)} taxa; environments: {len(ch.adapter.environments())}")
    cands = ch.discover(taxa, top_n=args.top_n)
    print(f"discovered {len(cands)} candidates\n")
    for cand in cands:
        out = ch.run(cand, by_ref)
        print(f"  [{out.significance.score:.2f}] {out.story.title}")
        print(f"      outcomes: {out.mc.outcomes}  valid_historical={out.overlap.valid_historical}")
        print(f"      ltx shots: {len(out.bundle.shots)}  canonicality={out.bundle.shots[0].canonicality.value if out.bundle.shots else 'n/a'}")
        if args.r2:
            key = ch.publish(out)
            print(f"      published -> r2:{key}")
    return 0


def _cmd_simulate(args: argparse.Namespace) -> int:
    """Full end-to-end stack simulation, fully offline (no LTX, no network).

    Runs: ingest -> evidence build -> discovery -> truth validity -> d20 battle
    -> Monte Carlo -> significance -> story -> shots -> LTX ShotSpec bundle,
    then writes the complete episode bundle (story + shots + renderer manifest)
    to disk, simulating the publish step without calling any renderer.
    """
    import json
    from pathlib import Path

    from .channels import get_channel

    ch = get_channel(args.channel, n_runs=args.runs, offline=True)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"## Simulating channel: {ch.theme} (offline, {args.runs} runs)\n")

    taxa = ch.ingest(limit=args.taxa)
    by_ref = {t.ref.key: t for t in taxa}
    print(f"step ingest    : {len(taxa)} taxa, {len(ch.manifest.reconstructions)} reconstructions, {len(ch.manifest.sources)} sources")
    cands = ch.discover(taxa, top_n=args.top_n)
    print(f"step discovery : {len(cands)} candidates")

    written = 0
    for cand in cands:
        out = ch.run(cand, by_ref)
        payload = {
            "channel": ch.theme,
            "candidate": {
                "template": cand.template,
                "entities": [f"{e.namespace}:{e.key}" for e in cand.entities],
                "mode": cand.mode,
            },
            "overlap": out.overlap.summary(),
            "valid_historical": out.overlap.valid_historical,
            "reconstructions": {
                k: {"version": r.version, "assertions": len(r.assertions)} for k, r in ch.manifest.reconstructions.items()
            },
            "monte_carlo": {"outcomes": out.mc.outcomes, "selected_runs": out.mc.selected, "master_seed": out.mc.master_seed},
            "significance": {"score": out.significance.score, "signals": out.significance.signals},
            "story": out.story.render(),
            "ltx": out.bundle.to_dict(),
        }
        stem = "_".join(e.key for e in cand.entities)
        fp = out_dir / f"{stem}_{cand.template}.json"
        fp.write_text(json.dumps(payload, indent=2))
        written += 1
        print(f"  [{out.significance.score:.2f}] {out.story.title}")
        print(f"      outcomes={out.mc.outcomes} valid={out.overlap.valid_historical} shots={len(out.bundle.shots)}")
        print(f"      wrote {fp.name}")

    print(f"\nsimulate complete: {written} episodes -> {out_dir}")
    return 0


def _cmd_snapshot(args: argparse.Namespace) -> int:
    """Build an immutable WorldSnapshot for a channel and print its digest."""
    from .channels import get_channel

    ch = get_channel(args.channel, offline=True)
    ch.ingest(limit=args.taxa)
    snap = ch.snapshot(world_id=args.world)
    print(f"world: {snap.world_id} v{snap.world_version}")
    print(f"entities: {len(snap.entities)} | digest: {snap.digest()}")
    return 0


def _cmd_produce(args: argparse.Namespace) -> int:
    from .production.produce import produce_episode

    res = produce_episode(
        args.channel,
        world_id=args.world,
        out_dir=args.out,
        n_runs=args.runs,
        resume_run=args.resume,
    )
    print(f"run: {res.run.run_id}")
    print(f"stages: {list(res.run.digests.keys())}")
    print(f"shots rendered: {len(res.render_jobs)} | QA: {len(res.qa)}")
    print(f"episode manifest digest: {res.episode_manifest.digest()}")
    print(f"assembly: {res.assembly['master']} master + {res.assembly['derivatives']} derivatives")
    return 0


def _cmd_resume(args: argparse.Namespace) -> int:
    from .production.produce import produce_episode

    res = produce_episode(args.channel, resume_run=args.run)
    print(f"resumed run {res.run.run_id} to {res.run.stage.value}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="monstah", description="world model engine")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scenarios", help="run scenario discovery on a corpus")
    s.add_argument("--top-n", type=int, default=10, dest="top_n")
    s.set_defaults(func=_cmd_scenarios)

    c = sub.add_parser("channel", help="run a themed channel end-to-end")
    c.add_argument("channel", help=f"one of: {', '.join(list_channels())}")
    c.add_argument("--taxa", type=int, default=40)
    c.add_argument("--top-n", type=int, default=5, dest="top_n")
    c.add_argument("--runs", type=int, default=1000, dest="runs")
    c.add_argument("--r2", action="store_true", help="publish render bundles to R2")
    c.set_defaults(func=_cmd_channel)

    sim = sub.add_parser("simulate", help="full offline end-to-end stack simulation")
    sim.add_argument("channel", help=f"one of: {', '.join(list_channels())}")
    sim.add_argument("--taxa", type=int, default=40)
    sim.add_argument("--top-n", type=int, default=5, dest="top_n")
    sim.add_argument("--runs", type=int, default=1000, dest="runs")
    sim.add_argument("--out", default="out/simulation", help="output directory")
    sim.set_defaults(func=_cmd_simulate)

    snap = sub.add_parser("snapshot", help="build an immutable WorldSnapshot + digest")
    snap.add_argument("channel", help=f"one of: {', '.join(list_channels())}")
    snap.add_argument("--taxa", type=int, default=40)
    snap.add_argument("--world", default="hell-creek")
    snap.set_defaults(func=_cmd_snapshot)

    prod = sub.add_parser("produce", help="one-command evidence-to-media vertical slice")
    prod.add_argument("channel", help=f"one of: {', '.join(list_channels())}")
    prod.add_argument("--world", default="hell-creek")
    prod.add_argument("--out", default="out/produce")
    prod.add_argument("--runs", type=int, default=500, dest="runs")
    prod.add_argument("--resume", default=None, help="resume a run id")
    prod.set_defaults(func=_cmd_produce)

    resume = sub.add_parser("resume", help="resume a production run from its manifest")
    resume.add_argument("channel", help=f"one of: {', '.join(list_channels())}")
    resume.add_argument("run", help="run id (path to RUN.json)")
    resume.set_defaults(func=_cmd_resume)

    i = sub.add_parser("ingest", help="ingest taxa from PBDB + Macrostrat")
    i.add_argument("taxa", nargs="*")
    i.add_argument("--cache", default="~/.cache/monstah")
    i.set_defaults(func=_cmd_ingest)

    m = sub.add_parser("matchup", help="Monte Carlo duel from two Open5e statblocks")
    m.add_argument("a", help="monster slug A")
    m.add_argument("b", help="monster slug B")
    m.add_argument("--runs", type=int, default=1000, dest="runs")
    m.add_argument("--cache", default="~/.cache/monstah")
    m.set_defaults(func=_cmd_matchup)

    r = sub.add_parser("run", help="run the full pipeline over discovered scenarios")
    r.add_argument("--top-n", type=int, default=5, dest="top_n")
    r.add_argument("--runs", type=int, default=500, dest="n_runs")
    r.add_argument("--r2", action="store_true", help="store bundles to R2")
    r.set_defaults(func=_cmd_run)

    args = p.parse_args(argv)
    return args.func(args)


def list_channels() -> list[str]:
    from .channels import list_channels as _lc

    return _lc()


if __name__ == "__main__":
    sys.exit(main())
