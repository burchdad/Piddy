#!/usr/bin/env python3
"""
CLI tool for running the Piddy KB ingestion pipeline.

Usage:
    python3 ingest_kb.py quick              # Test with 5 books
    python3 ingest_kb.py full --max 100     # Ingest up to 100 books
    python3 ingest_kb.py category web_development --max 30
"""

import argparse
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.kb.ingestion_pipeline import IngestionPipeline, SelectiveIngestion


def main():
    parser = argparse.ArgumentParser(
        description='Piddy KB Content Ingestion Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with 5 books
  python3 ingest_kb.py quick
  
  # Ingest 50 random books
  python3 ingest_kb.py full --max 50
  
  # Ingest Web Development category (30 books)
  python3 ingest_kb.py category web_development --max 30
  
  # Ingest Backend category
  python3 ingest_kb.py category backend --max 40
  
  # List available categories
  python3 ingest_kb.py categories
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Quick test command
    quick_parser = subparsers.add_parser('quick', help='Quick test ingestion (5 books)')
    quick_parser.set_defaults(func=cmd_quick)
    
    # Full ingestion command
    full_parser = subparsers.add_parser('full', help='Full book ingestion')
    full_parser.add_argument('--max', type=int, default=50, help='Max books to ingest')
    full_parser.set_defaults(func=cmd_full)
    
    # Category ingestion command
    cat_parser = subparsers.add_parser('category', help='Ingest specific category')
    cat_parser.add_argument('category', help='Category to ingest')
    cat_parser.add_argument('--max', type=int, default=30, help='Max books to ingest')
    cat_parser.set_defaults(func=cmd_category)
    
    # List categories command
    list_parser = subparsers.add_parser('categories', help='List available categories')
    list_parser.set_defaults(func=cmd_categories)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show ingestion status')
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


def cmd_quick(args):
    """Quick test ingestion."""
    print("\n" + "="*60)
    print("🧪 QUICK TEST: Ingesting 5 sample books")
    print("="*60 + "\n")
    
    stats = SelectiveIngestion.quick_test(num_books=5)
    return 0


def cmd_full(args):
    """Full ingestion."""
    print("\n" + "="*60)
    print(f"📚 FULL INGESTION: Up to {args.max} books")
    print("="*60 + "\n")
    
    pipeline = IngestionPipeline()
    stats = pipeline.ingest(max_books=args.max)
    return 0


def cmd_category(args):
    """Category-based ingestion."""
    print("\n" + "="*60)
    print(f"📚 CATEGORY INGESTION: {args.category}")
    print(f"   Max books: {args.max}")
    print("="*60 + "\n")
    
    try:
        stats = SelectiveIngestion.ingest_category(args.category, max_books=args.max)
        return 0
    except ValueError as e:
        logger.error(f"❌ {e}")
        cmd_categories(args)
        return 1


def cmd_categories(args):
    """List available categories."""
    print("\n" + "="*60)
    print("📋 AVAILABLE CATEGORIES")
    print("="*60 + "\n")
    
    categories = SelectiveIngestion.PRIORITY_CATEGORIES
    for cat, keywords in categories.items():
        print(f"  {cat.upper()}")
        print(f"    Keywords: {', '.join(keywords)}")
        print()
    
    return 0


def cmd_status(args):
    """Show ingestion status."""
    print("\n" + "="*60)
    print("📊 INGESTION STATUS")
    print("="*60 + "\n")
    
    pipeline = IngestionPipeline()
    progress = pipeline.progress
    
    print(f"Processed:  {len(progress.get('processed', []))} URLs")
    print(f"Failed:     {len(progress.get('failed', []))} URLs")
    
    # Show progress file location
    print(f"\nProgress file: {pipeline.progress_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
