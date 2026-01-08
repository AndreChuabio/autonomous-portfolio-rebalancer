"""
Autonomous Rebalancing Agent - CLI Interface
Main entry point for the rebalancing agent system.
"""

import argparse
import sys
from datetime import datetime

from src.workflows.rebalance_workflow import RebalanceWorkflow
from src.models.decision import DecisionStatus
from src.agents.sentiment_analyzer_agent import analyze_sentiment_cli


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Rebalancing Agent for PORT_A_TechGrowth",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --run              Execute one rebalancing workflow cycle
  python main.py --history          Show recent decision history
  python main.py --export decision.json  Export last decision to file
  python main.py --analyze-sentiment     Analyze sentiment for all portfolio tickers
  python main.py --analyze-sentiment --tickers AAPL NVDA --days 7  Analyze specific tickers
        """
    )

    parser.add_argument(
        '--run',
        action='store_true',
        help='Execute one complete rebalancing workflow cycle'
    )

    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Continuous monitoring mode (not yet implemented)'
    )

    parser.add_argument(
        '--history',
        action='store_true',
        help='Show recent decision history'
    )

    parser.add_argument(
        '--export',
        type=str,
        metavar='FILEPATH',
        help='Export last decision to JSON file'
    )

    parser.add_argument(
        '--analyze-sentiment',
        action='store_true',
        help='Run sentiment analysis on portfolio tickers (enriches Neo4j)'
    )

    parser.add_argument(
        '--tickers',
        type=str,
        nargs='+',
        help='Specific tickers to analyze (default: all portfolio tickers)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Lookback period for sentiment analysis (default: 30 days)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-analysis of articles with existing sentiment'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Number of decisions to show in history (default: 10)'
    )

    args = parser.parse_args()

    if not any([args.run, args.monitor, args.history, args.export, args.analyze_sentiment]):
        parser.print_help()
        sys.exit(1)

    workflow = RebalanceWorkflow()

    if args.analyze_sentiment:
        analyze_sentiment(args.tickers, args.days, args.force)

    elif args.run:
        run_workflow(workflow, args.export)

    elif args.history:
        show_history(workflow, args.limit)

    elif args.monitor:
        print("Continuous monitoring mode not yet implemented.")
        print("Use --run for single cycle execution.")
        sys.exit(1)

    elif args.export and not args.run:
        print("Error: --export requires --run to generate a decision first.")
        sys.exit(1)


def run_workflow(workflow: RebalanceWorkflow, export_path: str = None):
    """
    Execute one workflow cycle.

    Args:
        workflow: RebalanceWorkflow instance
        export_path: Optional path to export decision
    """
    try:
        decision = workflow.run_cycle()

        if export_path:
            workflow.export_decision(decision, export_path)

        if decision.decision_status == DecisionStatus.EXECUTE:
            print("\nNext Steps:")
            print("1. Review execution plan above")
            print("2. Execute trades manually or via paper trading MCP")
            print("3. Monitor execution and log outcomes")

    except Exception as e:
        print(f"\nError during workflow execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def show_history(workflow: RebalanceWorkflow, limit: int = 10):
    """
    Show recent decision history.

    Args:
        workflow: RebalanceWorkflow instance
        limit: Number of decisions to show
    """
    decisions = workflow.get_decision_history(limit)

    if not decisions:
        print("No decision history available.")
        return

    print("=" * 80)
    print(f"DECISION HISTORY (Last {len(decisions)} decisions)")
    print("=" * 80)

    for i, decision in enumerate(decisions, 1):
        print(f"\n{i}. Decision ID: {decision.decision_id}")
        print(
            f"   Timestamp: {decision.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Status: {decision.decision_status.value}")

        if decision.chosen_scenario:
            print(
                f"   Scenario: {decision.chosen_scenario.scenario_type.value}")
            print(f"   Trades: {decision.chosen_scenario.num_trades}")
            print(
                f"   Capital: ${decision.chosen_scenario.total_capital:,.0f}")

        print(f"   Confidence: {decision.confidence:.0%}")
        print(f"   Reasoning: {decision.reasoning[:100]}...")

    print("\n" + "=" * 80)


def analyze_sentiment(tickers: list = None, days: int = 30, force: bool = False):
    """
    Run sentiment analysis on portfolio tickers.

    Args:
        tickers: List of tickers to analyze (None = all portfolio)
        days: Lookback period
        force: Force re-analysis
    """
    print("\n" + "="*60)
    print("SENTIMENT ANALYZER - DATA ENRICHMENT MODE")
    print("="*60)
    print("\nThis tool analyzes articles and writes sentiment scores")
    print("back to Neo4j for use by the SentimentExplainerAgent.")
    print("\nNOTE: MCP write operations not yet implemented in server.")
    print("Current implementation shows structure only.\n")

    try:
        results = analyze_sentiment_cli(
            tickers=tickers, days=days, force=force)

        print("\n✓ Sentiment analysis complete")
        print(f"Ready to enrich {results.get('analyzed', 0)} articles")
        print("\nNext steps:")
        print("1. Implement MCP write operation: write_article_sentiment")
        print("2. Add Neo4j schema for copilot_sentiment relationship")
        print("3. Re-run this command to enrich database\n")

    except Exception as e:
        print(f"\n❌ Error during sentiment analysis: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
