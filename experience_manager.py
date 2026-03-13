#!/usr/bin/env python3
"""
CLI for managing Piddy's learned experiences and feeding them back into KB.

Usage:
    python3 experience_manager.py status              # See all experiences
    python3 experience_manager.py approve --id XXX    # Approve a fix
    python3 experience_manager.py feed-to-kb           # Move approved to KB
    python3 experience_manager.py stats                # See improvement stats
"""

import argparse
import logging
import sys
import json
from pathlib import Path
from tabulate import tabulate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.kb.experience_recorder import KBExperienceRecorder, ExperienceIntegrator


def main():
    parser = argparse.ArgumentParser(
        description='Piddy Experience Manager - Self-Growing KB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # See all learned experiences
  python3 experience_manager.py status
  
  # Approve a fix (mark as working)
  python3 experience_manager.py approve --id abc123 --quality 0.95
  
  # Feed approved experiences into KB
  python3 experience_manager.py feed-to-kb
  
  # See improvement statistics
  python3 experience_manager.py stats
  
  # Find high-value experiences ready for KB
  python3 experience_manager.py ready-for-kb
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show all experiences')
    status_parser.set_defaults(func=cmd_status)
    
    # Approve command
    approve_parser = subparsers.add_parser('approve', help='Approve an experience')
    approve_parser.add_argument('--id', required=True, help='Experience ID')
    approve_parser.add_argument('--quality', type=float, default=0.9, help='Quality score (0-1)')
    approve_parser.set_defaults(func=cmd_approve)
    
    # Feed to KB command
    feed_parser = subparsers.add_parser('feed-to-kb', help='Feed approved to KB')
    feed_parser.add_argument('--min-approvals', type=int, default=1)
    feed_parser.add_argument('--min-confidence', type=float, default=0.7)
    feed_parser.set_defaults(func=cmd_feed_to_kb)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=cmd_stats)
    
    # Ready for KB command
    ready_parser = subparsers.add_parser('ready-for-kb', help='Show experiences ready for KB')
    ready_parser.set_defaults(func=cmd_ready_for_kb)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export experiences as JSON')
    export_parser.add_argument('--filename', default='experiences.json')
    export_parser.set_defaults(func=cmd_export)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


def cmd_status(args):
    """Show all learned experiences."""
    print("\n" + "="*80)
    print("📚 PIDDY LEARNED EXPERIENCES")
    print("="*80 + "\n")
    
    recorder = KBExperienceRecorder()
    experiences = recorder.experiences
    
    if not experiences:
        print("No experiences recorded yet.\n")
        return 0
    
    table_data = []
    for exp_id, exp in experiences.items():
        table_data.append([
            exp_id[:8],
            exp.get('title', '')[:30],
            f"{exp.get('confidence', 0.0)*100:.0f}%",
            exp.get('approval_count', 0),
            f"{exp.get('success_rate', 0.0)*100:.0f}%",
            "✓ KB" if exp.get('in_kb') else "• Cache",
            ','.join(exp.get('tags', [])[:2])
        ])
    
    headers = ["ID", "Title", "Confidence", "Approvals", "Success", "Location", "Tags"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    print(f"\nTotal: {len(experiences)} experiences\n")
    return 0


def cmd_approve(args):
    """Approve a learned experience."""
    recorder = KBExperienceRecorder()
    
    success = recorder.approve_fix(args.id, success=True, quality_score=args.quality)
    
    if success:
        exp = recorder.experiences.get(args.id, {})
        print(f"\n✅ Approved: {exp.get('title')}")
        print(f"   Confidence: {exp.get('confidence', 0.0)*100:.0f}%")
        print(f"   Success Rate: {exp.get('success_rate', 0.0)*100:.0f}%")
        print(f"   Approvals: {exp.get('approval_count', 0)}\n")
        return 0
    else:
        print(f"❌ Could not approve experience: {args.id}\n")
        return 1


def cmd_feed_to_kb(args):
    """Feed approved experiences into KB."""
    print("\n" + "="*80)
    print("📥 FEEDING APPROVED EXPERIENCES TO KB")
    print("="*80 + "\n")
    
    recorder = KBExperienceRecorder()
    
    added = recorder.feed_all_approved_to_kb(
        min_approvals=args.min_approvals,
        min_confidence=args.min_confidence
    )
    
    stats = recorder.get_stats()
    print(f"\n📊 STATS")
    print(f"   Total Experiences: {stats['total_experiences']}")
    print(f"   In KB: {stats['in_kb']}")
    print(f"   Added This Run: {added}")
    print(f"   Approval Rate: {stats['approval_rate']*100:.0f}%")
    print(f"   Avg Success Rate: {stats['avg_success_rate']*100:.0f}%\n")
    
    return 0


def cmd_stats(args):
    """Show improvement statistics."""
    print("\n" + "="*80)
    print("📊 PIDDY SELF-IMPROVEMENT STATISTICS")
    print("="*80 + "\n")
    
    recorder = KBExperienceRecorder()
    stats = recorder.get_stats()
    
    print(f"Total Experiences Recorded: {stats['total_experiences']}")
    print(f"  ✓ Approved: {stats['approved']} ({stats['approval_rate']*100:.0f}%)")
    print(f"  ✓ High Confidence: {stats['high_confidence']}")
    print(f"  ✓ In Knowledge Base: {stats['in_kb']}\n")
    
    print(f"Quality Metrics:")
    print(f"  Average Success Rate: {stats['avg_success_rate']*100:.1f}%")
    print(f"  Knowledge Base Coverage: {stats['in_kb'] if stats['total_experiences'] > 0 else 0}/{stats['total_experiences']}\n")
    
    # Show by tag
    print(f"Experiences by Tag:")
    for tag in ['bug-fix', 'optimization', 'pattern', 'refactor']:
        exps = recorder.get_experiences_by_tag(tag)
        if exps:
            print(f"  • {tag}: {len(exps)} fixes")
    
    print()
    return 0


def cmd_ready_for_kb(args):
    """Show experiences ready to feed into KB."""
    print("\n" + "="*80)
    print("🎯 EXPERIENCES READY FOR KB")
    print("="*80 + "\n")
    
    recorder = KBExperienceRecorder()
    ready = recorder.get_high_value_experiences(
        min_confidence=0.75,
        min_approvals=1
    )
    
    if not ready:
        print("No experiences ready for KB yet.\n")
        return 0
    
    table_data = []
    for exp in ready:
        table_data.append([
            exp['experience_id'][:8],
            exp.get('title', '')[:30],
            f"{exp.get('confidence', 0.0)*100:.0f}%",
            exp.get('approval_count', 0),
            f"{exp.get('success_rate', 0.0)*100:.0f}%",
        ])
    
    headers = ["ID", "Title", "Confidence", "Approvals", "Success Rate"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    print(f"\n📥 Ready to feed: {len(ready)} experiences")
    print(f"   Run: python3 experience_manager.py feed-to-kb\n")
    
    return 0


def cmd_export(args):
    """Export experiences as JSON."""
    recorder = KBExperienceRecorder()
    
    export_data = {
        'timestamp': recorder.experiences_file.stat().st_mtime if recorder.experiences_file.exists() else 0,
        'total': len(recorder.experiences),
        'stats': recorder.get_stats(),
        'experiences': list(recorder.experiences.values())
    }
    
    with open(args.filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(recorder.experiences)} experiences to {args.filename}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
