#!/usr/bin/env python3
"""
Gary Bot Backup Manager
Standalone script for managing ChromaDB backups.
"""

import sys
import argparse
from pathlib import Path
from src.backup_system import BackupSystem
from src.config import get_config

def main():
    parser = argparse.ArgumentParser(description="Gary Bot Backup Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create backup command
    backup_parser = subparsers.add_parser('create', help='Create a new backup')
    backup_parser.add_argument('--include-embeddings', action='store_true', 
                              help='Include embeddings in JSON export')
    
    # List backups command
    list_parser = subparsers.add_parser('list', help='List all available backups')
    
    # Restore backup command
    restore_parser = subparsers.add_parser('restore', help='Restore from a backup')
    restore_parser.add_argument('backup_path', help='Path to backup file')
    restore_parser.add_argument('--overwrite', action='store_true',
                               help='Overwrite existing database')
    
    # Auto backup command
    auto_parser = subparsers.add_parser('auto', help='Create automatic backup with cleanup')
    auto_parser.add_argument('--max-backups', type=int, default=10,
                            help='Maximum number of backups to keep (default: 10)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export posts to JSON')
    export_parser.add_argument('--output', help='Output file path')
    export_parser.add_argument('--include-embeddings', action='store_true',
                              help='Include embeddings in export')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize backup system
    config = get_config()
    backup_system = BackupSystem(config.db_path)
    
    try:
        if args.command == 'create':
            backup_path = backup_system.create_backup(include_embeddings=args.include_embeddings)
            print(f"📦 Backup created: {backup_path}")
            
        elif args.command == 'list':
            backups = backup_system.list_backups()
            if not backups:
                print("📭 No backups found")
            else:
                print(f"📋 Found {len(backups)} backup(s):")
                for backup in backups:
                    print(f"  • {backup['filename']} ({backup['size_mb']} MB) - {backup['created_at']}")
                    
        elif args.command == 'restore':
            success = backup_system.restore_backup(args.backup_path, overwrite=args.overwrite)
            if success:
                print("✅ Backup restored successfully")
            else:
                print("❌ Failed to restore backup")
                sys.exit(1)
                
        elif args.command == 'auto':
            backup_path = backup_system.auto_backup(max_backups=args.max_backups)
            print(f"🔄 Auto backup completed: {backup_path}")
            
        elif args.command == 'export':
            export_path = backup_system.export_posts_json(
                output_path=args.output,
                include_embeddings=args.include_embeddings
            )
            print(f"📄 Posts exported: {export_path}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 