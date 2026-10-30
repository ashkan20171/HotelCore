"""Safe, headless maintenance commands. Does not start the Qt application."""
import argparse
import json
from pathlib import Path
from enterprise_maintenance import database_health, create_consistent_backup

def main(argv=None):
    parser = argparse.ArgumentParser(description='Ashkan Hotel Pro Enterprise maintenance')
    parser.add_argument('--database',type=Path,default=Path(__file__).with_name('hotel.db'))
    sub = parser.add_subparsers(dest='command',required=True)
    sub.add_parser('health',help='Check SQLite integrity and essential tables')
    backup = sub.add_parser('backup',help='Create a validated, consistent SQLite backup')
    backup.add_argument('--output-dir',required=True,type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command=='health':
            report=database_health(args.database)
            print(json.dumps(report,ensure_ascii=False,indent=2))
            return 0 if report['ok'] else 2
        output=create_consistent_backup(args.database,args.output_dir)
        print(f'Validated backup created: {output}')
        return 0
    except (OSError,ValueError,RuntimeError) as exc:
        parser.exit(2,f'Maintenance failed: {exc}\n')

if __name__=='__main__':
    raise SystemExit(main())
