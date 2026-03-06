"""
Phase 5 - Advanced DevOps & MLOps Integration CLI interface.
Main entry point for Phase 5 features.
"""
import sys
import json
import logging
from typing import Optional
from pathlib import Path

from .core import Phase5Core
from .ml_ops_handler import get_ml_ops_handler
from .observability import get_observability_manager
from .iac.validator import get_iac_validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase5CLI:
    """CLI interface for Phase 5 capabilities."""

    def __init__(self):
        """Initialize Phase 5 CLI."""
        self.core = Phase5Core()
        self.ml_ops = get_ml_ops_handler()
        self.observability = get_observability_manager()
        self.iac_validator = get_iac_validator()
        logger.info("✅ Phase 5 CLI initialized")

    def run(self, args: list) -> int:
        """
        Run Phase 5 CLI.

        Args:
            args: Command line arguments

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        if not args or args[0] in ["-h", "--help"]:
            self.print_help()
            return 0

        command = args[0]

        try:
            if command == "status":
                return self.cmd_status(args[1:])
            elif command == "ml":
                return self.cmd_ml_ops(args[1:])
            elif command == "observe":
                return self.cmd_observability(args[1:])
            elif command == "iac":
                return self.cmd_iac_validate(args[1:])
            elif command == "version":
                return self.cmd_version(args[1:])
            else:
                print(f"Unknown command: {command}")
                self.print_help()
                return 1
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return 1

    def cmd_status(self, args: list) -> int:
        """Show Phase 5 status and capabilities."""
        print("\n" + "=" * 60)
        print("🚀 PHASE 5 - Advanced DevOps & MLOps Integration")
        print("=" * 60)

        status = self.core.get_status()
        print(f"\nVersion: {status['version']}")
        print(f"Status: ✅ {status['status']}")
        print(f"Build Date: {status['build_date']}")

        print("\n📦 Available Features:")
        for feature in status['features']:
            print(f"  ✓ {feature}")

        print("\n🔧 Capabilities:")
        print("  • MLOps: Model training, evaluation, deployment")
        print("  • Observability: Metrics, logging, tracing")
        print("  • IaC Validation: Terraform, Kubernetes, Docker validation")
        print("  • Advanced Monitoring: Multi-cloud observability")
        print("  • CI/CD Integration: Automated pipeline management")

        print("\n💡 Try:")
        print("  phase5 ml --help          # MLOps operations")
        print("  phase5 observe --help     # Observability features")
        print("  phase5 iac --help         # IaC validation")

        print("\n" + "=" * 60)
        return 0

    def cmd_ml_ops(self, args: list) -> int:
        """Handle ML Ops commands."""
        if not args or args[0] in ["-h", "--help"]:
            print("\n📊 MLOps Commands:")
            print("  ml train <config>       Train ML model")
            print("  ml evaluate <model>     Evaluate model")
            print("  ml deploy <model>       Deploy model")
            print("  ml experiment <name>    Track experiment")
            return 0

        subcommand = args[0]

        if subcommand == "train":
            print("🎓 Starting ML training pipeline...")
            config_file = args[1] if len(args) > 1 else "model_config.yaml"
            result = self.ml_ops.train_model(config_file)
            print(json.dumps(result, indent=2))
            return 0

        elif subcommand == "evaluate":
            print("📈 Evaluating model...")
            model_path = args[1] if len(args) > 1 else "model.pkl"
            result = self.ml_ops.evaluate_model(model_path)
            print(json.dumps(result, indent=2))
            return 0

        elif subcommand == "deploy":
            print("🚀 Deploying model...")
            model_path = args[1] if len(args) > 1 else "model.pkl"
            result = self.ml_ops.deploy_model(model_path)
            print(json.dumps(result, indent=2))
            return 0

        else:
            print(f"Unknown ml subcommand: {subcommand}")
            return 1

    def cmd_observability(self, args: list) -> int:
        """Handle observability commands."""
        if not args or args[0] in ["-h", "--help"]:
            print("\n📊 Observability Commands:")
            print("  observe metrics         Show metrics")
            print("  observe logs <level>    Show logs")
            print("  observe traces          Show traces")
            print("  observe health          Service health check")
            return 0

        subcommand = args[0]

        if subcommand == "metrics":
            print("📊 Collecting metrics...")
            metrics = self.observability.collect_metrics()
            print(json.dumps(metrics, indent=2))
            return 0

        elif subcommand == "logs":
            level = args[1] if len(args) > 1 else "INFO"
            print(f"📝 Logs (level: {level}):")
            logs = self.observability.get_logs(level)
            for log in logs:
                print(f"  {log}")
            return 0

        elif subcommand == "traces":
            print("🔍 Distributed traces:")
            traces = self.observability.get_traces()
            print(json.dumps(traces, indent=2))
            return 0

        elif subcommand == "health":
            print("🏥 Health check:")
            health = self.observability.health_check()
            print(json.dumps(health, indent=2))
            return 0

        else:
            print(f"Unknown observe subcommand: {subcommand}")
            return 1

    def cmd_iac_validate(self, args: list) -> int:
        """Handle IaC validation commands."""
        if not args or args[0] in ["-h", "--help"]:
            print("\n🏗️  IaC Validation Commands:")
            print("  iac terraform <file>    Validate Terraform")
            print("  iac docker <file>       Validate Dockerfile")
            print("  iac k8s <file>          Validate Kubernetes")
            return 0

        if len(args) < 2:
            print("Error: Please specify file to validate")
            return 1

        file_type = args[0]
        file_path = args[1]

        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            return 1

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            if file_type == "terraform":
                result = self.iac_validator.validate_terraform(content)
            elif file_type == "docker":
                result = self.iac_validator.validate_dockerfile(content)
            elif file_type in ["k8s", "kubernetes"]:
                result = self.iac_validator.validate_kubernetes(content)
            else:
                print(f"Unknown IaC format: {file_type}")
                return 1

            print(f"\n🏗️  IaC Validation Results ({file_type.upper()})")
            print("=" * 50)
            print(f"Quality Score: {result['quality_score']:.1f}/100")
            print(f"Issues: {sum(result['severity_count'].values())}")

            if result['severity_count']['critical'] > 0:
                print(f"  🔴 Critical: {result['severity_count']['critical']}")
            if result['severity_count']['high'] > 0:
                print(f"  🟠 High: {result['severity_count']['high']}")
            if result['severity_count']['medium'] > 0:
                print(f"  🟡 Medium: {result['severity_count']['medium']}")
            if result['severity_count']['low'] > 0:
                print(f"  🟢 Low: {result['severity_count']['low']}")

            print("\nRecommendations:")
            for rec in result['recommendations']:
                print(f"  {rec}")

            if result['issues']:
                print("\nIssues:")
                for issue in result['issues']:
                    severity_emoji = {"critical": "🔴", "high": "🟠", 
                                     "medium": "🟡", "low": "🟢"}
                    emoji = severity_emoji.get(issue['severity'], "❓")
                    print(f"  {emoji} [{issue['category']}] {issue['message']}")
                    if issue['suggestion']:
                        print(f"     💡 {issue['suggestion']}")

            return 0

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return 1

    def cmd_version(self, args: list) -> int:
        """Show version information."""
        status = self.core.get_status()
        print(f"Phase 5 version {status['version']}")
        print(f"Build date: {status['build_date']}")
        return 0

    def print_help(self):
        """Print help message."""
        help_text = """
Phase 5 - Advanced DevOps & MLOps Integration

Usage: phase5 <command> [options]

Commands:
  status              Show Phase 5 status and capabilities
  ml                  MLOps operations
  observe             Observability features
  iac                 IaC validation
  version             Show version
  -h, --help          Show this help message

Examples:
  phase5 status               # Show capabilities
  phase5 ml train config.yaml # Train ML model
  phase5 observe metrics      # Show metrics
  phase5 iac terraform main.tf # Validate Terraform

For more information on a command:
  phase5 <command> --help
"""
        print(help_text)


def main() -> int:
    """Main entry point."""
    cli = Phase5CLI()
    return cli.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
