"""CLI — pykworldsim run config.yaml --steps 100 --dt 0.016 --seed 42 --debug"""
from __future__ import annotations
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from pykworldsim.core.config.loader import ConfigLoader
from pykworldsim.core.components.position import Position
from pykworldsim.core.components.velocity import Velocity
from pykworldsim.core.components.person import Person
from pykworldsim.plugins.registry import PluginRegistry

app = typer.Typer(name="pykworldsim", help="🌍 ECS World Simulation Framework v3", add_completion=False)
console = Console()


@app.command()
def run(
    config: str   = typer.Argument(...,           help="Path to YAML or JSON config file"),
    steps:  int   = typer.Option(None, "--steps", help="Override config simulation steps"),
    dt:     float = typer.Option(None, "--dt",    help="Override config time delta"),
    seed:   int   = typer.Option(None, "--seed",  help="Override config random seed"),
    save:   str   = typer.Option(None, "--save",  help="Save final world state to JSON path"),
    debug:  bool  = typer.Option(False,"--debug", help="Enable DEBUG logging"),
    report: bool  = typer.Option(False,"--report",help="Print full world report as JSON"),
    plugin: list[str] = typer.Option([], "--plugin", help="Dotted path to custom system class"),
) -> None:
    """Run a simulation from a YAML or JSON config file."""
    from pykworldsim.utils import configure_logging
    configure_logging("DEBUG" if debug else "INFO")

    for p in plugin:
        try:
            PluginRegistry.register_from_path(p)
            console.print(f"[dim]Plugin loaded:[/] {p}")
        except Exception as exc:
            console.print(f"[red]Plugin error {p!r}:[/] {exc}")
            raise typer.Exit(1)

    try:
        cfg = ConfigLoader.load(config)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/] {exc}"); raise typer.Exit(1)

    # CLI overrides take precedence over config file values
    if steps is not None: cfg.simulation.steps = steps
    if dt    is not None: cfg.simulation.dt    = dt
    if seed  is not None: cfg.simulation.seed  = seed

    world, sim = ConfigLoader.build(cfg)

    console.print(
        f"\n[bold green]▶ pykworldsim v3[/]  world=[cyan]{world.name}[/]  "
        f"steps=[yellow]{cfg.simulation.steps}[/]  dt=[yellow]{cfg.simulation.dt}[/]  "
        f"seed=[yellow]{cfg.simulation.seed}[/]\n"
    )

    sim.run(steps=cfg.simulation.steps, dt=cfg.simulation.dt)

    table = Table(title=f"World state after {sim.tick} ticks | elapsed={sim.elapsed:.3f}s")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Position (x, y)", style="green")
    table.add_column("Velocity (dx, dy)", style="yellow")
    table.add_column("Happiness / Energy", style="magenta")

    for entity in sorted(world.entities, key=lambda e: e.id):
        pos_s = vel_s = hap_s = name_s = "—"
        if world.has_component(entity, Position):
            p = world.get_component(entity, Position)
            pos_s = f"({p.x:.3f}, {p.y:.3f})"
        if world.has_component(entity, Velocity):
            v = world.get_component(entity, Velocity)
            vel_s = f"({v.dx:.3f}, {v.dy:.3f})"
        if world.has_component(entity, Person):
            pr = world.get_component(entity, Person)
            name_s = pr.name
            hap_s = f"{pr.happiness:.1f} / {pr.energy:.1f}"
        table.add_row(str(entity.id), name_s, pos_s, vel_s, hap_s)

    console.print(table)
    if save:
        world.save(save)
        console.print(f"\n[bold]💾 World saved →[/] {save}")
    if report:
        rprint(world.generate_report())


@app.command()
def inspect(save_file: str = typer.Argument(..., help="Path to a world JSON save file")) -> None:
    """Inspect a previously saved world state."""
    from pykworldsim.core.world import World
    try:
        world = World.load(save_file)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/] {exc}"); raise typer.Exit(1)
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
