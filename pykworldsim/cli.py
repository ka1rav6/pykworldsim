"""CLI entry-point: ``pykworldsim run config.yaml``"""
from __future__ import annotations

import json
import sys

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from pykworldsim.core.config.loader import ConfigLoader
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.plugins.registry import PluginRegistry

app = typer.Typer(
    name="pykworldsim",
    help="🌍 ECS World Simulation Framework",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    config: str = typer.Argument(..., help="Path to YAML or JSON config file"),
    save: str = typer.Option(None, "--save", "-s", help="Save final world state to this JSON path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable DEBUG logging"),
    report: bool = typer.Option(False, "--report", "-r", help="Print full world report as JSON"),
    plugin: list[str] = typer.Option([], "--plugin", "-p", help="Dotted path to a custom system class (repeatable)"),
) -> None:
    """Run a simulation defined by a YAML or JSON config file."""
    from pykworldsim.utils import configure_logging
    configure_logging("DEBUG" if verbose else "INFO")

    # Load plugins before building the world
    for p in plugin:
        try:
            PluginRegistry.register_from_path(p)
            console.print(f"[dim]Plugin loaded:[/] {p}")
        except Exception as exc:
            console.print(f"[red]Failed to load plugin {p!r}: {exc}[/]")
            raise typer.Exit(1)

    try:
        cfg = ConfigLoader.load(config)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/] {exc}")
        raise typer.Exit(1)

    world, sim = ConfigLoader.build(cfg)

    console.print(
        f"\n[bold green]▶ pykworldsim[/]  world=[cyan]{world.name}[/]  "
        f"steps=[yellow]{cfg.simulation.steps}[/]  dt=[yellow]{cfg.simulation.dt}[/]  "
        f"seed=[yellow]{cfg.simulation.seed}[/]\n"
    )

    sim.run(steps=cfg.simulation.steps, dt=cfg.simulation.dt)

    # ── Results table ──────────────────────────────────────────────────
    table = Table(title=f"World state after {sim.tick} ticks | elapsed={sim.elapsed:.3f}s")
    table.add_column("ID",      style="dim",    no_wrap=True)
    table.add_column("Name",    style="cyan")
    table.add_column("Position (x, y)",  style="green")
    table.add_column("Velocity (dx, dy)", style="yellow")
    table.add_column("Happiness / Energy", style="magenta")

    for entity in sorted(world.entities, key=lambda e: e.id):
        pos_str = vel_str = hap_str = name_str = "—"

        if world.has_component(entity, Position):
            p = world.get_component(entity, Position)
            pos_str = f"({p.x:.3f}, {p.y:.3f})"
        if world.has_component(entity, Velocity):
            v = world.get_component(entity, Velocity)
            vel_str = f"({v.dx:.3f}, {v.dy:.3f})"
        if world.has_component(entity, Person):
            pr = world.get_component(entity, Person)
            name_str = pr.name
            hap_str = f"{pr.happiness:.1f} / {pr.energy:.1f}"

        table.add_row(str(entity.id), name_str, pos_str, vel_str, hap_str)

    console.print(table)

    if save:
        world.save(save)
        console.print(f"\n[bold]💾 World saved →[/] {save}")

    if report:
        console.print("\n[bold]Full report:[/]")
        rprint(world.generate_report())


@app.command()
def inspect(
    save_file: str = typer.Argument(..., help="Path to a world JSON save file"),
) -> None:
    """Inspect a previously saved world state."""
    from pykworldsim.core.world import World

    try:
        world = World.load(save_file)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/] {exc}")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]World:[/] {world.name}  |  entities: {len(world.entities)}\n")
    rprint(world.generate_report())


@app.command()
def plugins() -> None:
    """List all registered plugin systems."""
    names = PluginRegistry.list_names()
    if not names:
        console.print("[dim]No plugins registered.[/]")
    else:
        for n in names:
            console.print(f"  • {n}")


if __name__ == "__main__":
    app()
