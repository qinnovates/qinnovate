"""
TARA Command Line Interface

Telemetry Analysis & Response Automation

Provides CLI access to TARA functionality:
- Launch web dashboard
- Run simulations
- Execute attack scenarios
- Monitor neural signals
"""

import argparse
import sys
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="tara",
        description="TARA - Telemetry Analysis & Response Automation for neural security",
        epilog="For more information, visit: https://github.com/qinnovates/mindloft",
    )

    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version information",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # UI command
    ui_parser = subparsers.add_parser("ui", help="Launch the web dashboard")
    ui_parser.add_argument(
        "--port", "-p",
        type=int,
        default=8501,
        help="Port to run the dashboard on (default: 8501)",
    )
    ui_parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)",
    )
    ui_parser.add_argument(
        "--browser",
        action="store_true",
        default=True,
        help="Open browser automatically (default: True)",
    )
    ui_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically",
    )

    # Simulate command
    sim_parser = subparsers.add_parser("simulate", help="Run neural network simulation")
    sim_parser.add_argument(
        "--network", "-n",
        type=str,
        choices=["oni", "recurrent", "small-world"],
        default="oni",
        help="Network type to simulate (default: oni)",
    )
    sim_parser.add_argument(
        "--neurons",
        type=int,
        default=200,
        help="Number of neurons (default: 200)",
    )
    sim_parser.add_argument(
        "--duration", "-d",
        type=float,
        default=1000.0,
        help="Simulation duration in ms (default: 1000)",
    )
    sim_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for results (JSON format)",
    )
    sim_parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility",
    )

    # Attack command
    attack_parser = subparsers.add_parser("attack", help="Run attack simulation")
    attack_parser.add_argument(
        "--scenario", "-s",
        type=str,
        choices=["ransomware", "gateway_infiltration", "dos", "mitm", "recon"],
        required=True,
        help="Attack scenario to simulate",
    )
    attack_parser.add_argument(
        "--target", "-t",
        type=str,
        help="Target network file (JSON)",
    )
    attack_parser.add_argument(
        "--intensity", "-i",
        type=float,
        default=0.7,
        help="Attack intensity 0-1 (default: 0.7)",
    )
    attack_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for attack report",
    )

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor neural signals")
    monitor_parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input signal file to monitor",
    )
    monitor_parser.add_argument(
        "--realtime",
        action="store_true",
        help="Enable real-time monitoring mode",
    )
    monitor_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for monitoring results",
    )
    monitor_parser.add_argument(
        "--rules",
        type=str,
        help="Custom rules file (JSON)",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List available resources")
    list_parser.add_argument(
        "resource",
        choices=["patterns", "scenarios", "rules", "networks"],
        help="Resource type to list",
    )

    return parser


def cmd_version():
    """Show version information."""
    from tara_mvp import __version__, __name_full__
    print(f"TARA v{__version__}")
    print(f"{__name_full__}")
    print()
    print("Named after Tara, the Buddhist goddess of protection")
    print("who guides travelers safely through darkness.")
    print()
    print("Components:")
    print("  - Core: ONI Framework security primitives")
    print("  - Simulation: Neural network simulation engine")
    print("  - Attacks: Attack pattern generator")
    print("  - NSAM: Neural Signal Assurance Monitoring")
    print("  - UI: Web-based dashboard")


def cmd_ui(args):
    """Launch the web dashboard."""
    try:
        import streamlit.web.cli as stcli
    except ImportError:
        print("Error: Streamlit is required for the UI.")
        print("Install with: pip install tara-neural[ui]")
        sys.exit(1)

    import os
    app_path = os.path.join(os.path.dirname(__file__), "ui", "app.py")

    sys_argv = ["streamlit", "run", app_path]
    sys_argv.extend(["--server.port", str(args.port)])
    sys_argv.extend(["--server.address", args.host])

    if args.no_browser:
        sys_argv.extend(["--server.headless", "true"])

    print(f"Launching TARA Dashboard on {args.host}:{args.port}...")
    sys.argv = sys_argv
    stcli.main()


def cmd_simulate(args):
    """Run neural network simulation."""
    print(f"Running {args.network} simulation...")
    print(f"  Neurons: {args.neurons}")
    print(f"  Duration: {args.duration} ms")

    try:
        from tara_mvp.simulation import LayeredNetwork, RecurrentNetwork, SmallWorldNetwork
        from tara_mvp.simulation.engine import Simulator, NeuralRecorder

        # Create network
        if args.network == "oni":
            network = LayeredNetwork.create_oni_model(n_per_layer=args.neurons // 14)
        elif args.network == "recurrent":
            network = RecurrentNetwork(n_excitatory=int(args.neurons * 0.8),
                                       n_inhibitory=int(args.neurons * 0.2))
        else:
            network = SmallWorldNetwork(n_neurons=args.neurons)

        # Create simulator
        recorder = NeuralRecorder(record_spikes=True, record_states=True)
        sim = Simulator(network=network, recorder=recorder, seed=args.seed)

        # Run simulation
        print("Running simulation...")
        sim.run(duration=args.duration)

        # Get results
        results = recorder.get_results()
        print(f"\nResults:")
        print(f"  Total spikes: {results.get('total_spikes', 'N/A')}")
        print(f"  Average rate: {results.get('average_rate', 'N/A'):.1f} Hz")

        # Save output
        if args.output:
            import json
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to: {args.output}")

    except ImportError as e:
        print(f"Error: Missing dependencies - {e}")
        print("Install with: pip install tara-neural[simulation]")
        sys.exit(1)
    except Exception as e:
        print(f"Simulation error: {e}")
        sys.exit(1)


def cmd_attack(args):
    """Run attack simulation."""
    print(f"Running attack scenario: {args.scenario}")
    print(f"  Intensity: {args.intensity}")

    try:
        from tara_mvp.attacks import AttackSimulator
        from tara_mvp.attacks.scenarios import get_scenario

        simulator = AttackSimulator()
        scenario = get_scenario(args.scenario)

        # Load target network if provided
        network = None
        if args.target:
            print(f"  Target: {args.target}")
            # Would load network from file here

        # Run attack
        print("\nExecuting attack simulation...")
        result = simulator.run_scenario(scenario, network=network)

        # Print results
        print("\n" + "=" * 50)
        print("TARA ATTACK SIMULATION RESULTS")
        print("=" * 50)
        print(f"Scenario: {result.scenario_name}")
        print(f"Duration: {result.duration:.1f} ms")
        print(f"Total Attacks: {result.total_attacks}")
        print(f"Detected: {result.detected_count} ({result.detection_rate:.1%})")
        print(f"Blocked: {result.blocked_count} ({result.block_rate:.1%})")

        print("\nTimeline:")
        for event in result.events:
            status = "BLOCKED" if event.blocked else ("DETECTED" if event.detected else "UNDETECTED")
            print(f"  {event.timestamp:8.1f}ms | {event.stage_name:20} | {status}")

        # Generate and save report
        report = simulator.generate_report(result)
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"\nReport saved to: {args.output}")

    except Exception as e:
        print(f"Attack simulation error: {e}")
        sys.exit(1)


def cmd_monitor(args):
    """Run neural monitoring."""
    print("Starting TARA neural monitor...")

    try:
        from tara_mvp.nsam import NeuralMonitor

        monitor = NeuralMonitor(name="TARA")

        if args.rules:
            print(f"Loading rules from: {args.rules}")
            # Would load custom rules here

        if args.realtime:
            print("Real-time monitoring mode enabled")
            print("Press Ctrl+C to stop")

            session = monitor.start()
            print(f"Session: {session.session_id}")

            try:
                import time
                import numpy as np

                while True:
                    # Simulate incoming metrics
                    metrics = {
                        "coherence": np.random.uniform(0.6, 0.95),
                        "spike_rate": np.random.uniform(30, 80),
                        "amplitude": np.random.uniform(40, 60),
                    }

                    result = monitor.process(metrics)
                    if result and result.detected:
                        print(f"[ALERT] {result.anomaly_type} (conf: {result.confidence:.2f})")

                    time.sleep(1)

            except KeyboardInterrupt:
                print("\nStopping monitor...")
                session = monitor.stop()
                print(f"\nSession Summary:")
                print(f"  Duration: {session.duration:.1f}s")
                print(f"  Samples: {session.samples_processed}")
                print(f"  Anomalies: {session.anomalies_detected}")
                print(f"  Alerts: {session.alerts_generated}")

        elif args.input:
            print(f"Processing input file: {args.input}")
            # Would process input file here

        else:
            print("Specify --realtime or --input to start monitoring")

    except Exception as e:
        print(f"Monitoring error: {e}")
        sys.exit(1)


def cmd_list(args):
    """List available resources."""
    if args.resource == "patterns":
        from tara_mvp.attacks.patterns import list_patterns, ATTACK_PATTERNS
        print("Available Attack Patterns:")
        print("-" * 40)
        for name in list_patterns():
            pattern = ATTACK_PATTERNS[name]
            print(f"  {name}")
            print(f"    Type: {pattern.attack_type.name}")
            print(f"    Layer: L{pattern.target_layer}")
            print(f"    Intensity: {pattern.intensity}")
            print()

    elif args.resource == "scenarios":
        from tara_mvp.attacks.scenarios import list_scenarios, PREDEFINED_SCENARIOS
        print("Available Attack Scenarios:")
        print("-" * 40)
        for name in list_scenarios():
            scenario = PREDEFINED_SCENARIOS[name]
            print(f"  {name}")
            print(f"    Name: {scenario.name}")
            print(f"    Severity: {scenario.severity.name}")
            print(f"    Stages: {scenario.n_stages}")
            print()

    elif args.resource == "rules":
        from tara_mvp.nsam.rules import list_rules, PREDEFINED_RULES
        print("Available Detection Rules:")
        print("-" * 40)
        for rule_id in list_rules():
            rule = PREDEFINED_RULES[rule_id]
            print(f"  {rule_id}")
            print(f"    Name: {rule.name}")
            print(f"    Type: {rule.rule_type.name}")
            print(f"    Tags: {', '.join(rule.tags)}")
            print()

    elif args.resource == "networks":
        print("Available Network Types:")
        print("-" * 40)
        print("  oni          - ONI 14-Layer Model (aligned with framework)")
        print("  recurrent    - Recurrent E/I Balanced Network")
        print("  small-world  - Watts-Strogatz Small-World Network")


def main(argv: Optional[List[str]] = None):
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.version:
        cmd_version()
        return

    if args.command is None:
        parser.print_help()
        return

    commands = {
        "ui": cmd_ui,
        "simulate": cmd_simulate,
        "attack": cmd_attack,
        "monitor": cmd_monitor,
        "list": cmd_list,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
