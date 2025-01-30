"""
Command-line interface for checking dependencies
"""
import sys
from modules.package_fix.dependency_checker import check_all_dependencies
from modules.package_fix.installers import install_dependencies
import argparse

def main():
    parser = argparse.ArgumentParser(description='Check and install dependencies for AI-Chat-App')
    parser.add_argument('--module', help='Check specific module dependencies')
    parser.add_argument('--install', action='store_true', help='Install missing dependencies')
    parser.add_argument('--quiet', action='store_true', help='Suppress output')
    
    args = parser.parse_args()
    
    if args.install:
        return 0 if install_dependencies(args.module, verbose=not args.quiet) else 1
    else:
        return 0 if check_all_dependencies(args.module, verbose=not args.quiet) else 1

if __name__ == "__main__":
    sys.exit(main())