"""
Compatibility launcher for easy_scanner.py.

Usage examples (run from the project root):
    python scripts/easyscan.py
    python scripts/easyscan.py --auto --target http://localhost:5002
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import easy_scanner as scanner


if __name__ == "__main__":
    os.chdir(scanner.PROJECT_ROOT)
    args = scanner.parse_cli_args()
    try:
        if args.auto:
            success = scanner.run_auto_scan(args)
            if not success:
                sys.exit(1)
        else:
            scanner.main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
