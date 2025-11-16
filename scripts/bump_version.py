#!/usr/bin/env python3
"""Script to bump version numbers across the project."""

import argparse
import re
from pathlib import Path


def bump_version(current_version: str, bump_type: str) -> str:
    """
    Bump version number based on type.
    
    Args:
        current_version: Current version string (e.g., "0.1.0")
        bump_type: Type of bump ("major", "minor", "patch")
    
    Returns:
        New version string
    """
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"


def update_version_file(new_version: str):
    """Update the __version__.py file."""
    version_file = Path("src/meshtastic_mqtt_cli/__version__.py")
    content = f'''"""Version information for Meshtastic MQTT CLI."""

__version__ = "{new_version}"
__version_info__ = tuple(int(i) for i in __version__.split(".") if i.isdigit())
'''
    version_file.write_text(content)
    print(f"✓ Updated {version_file}")


def update_changelog(new_version: str):
    """Update CHANGELOG.md with new version."""
    changelog = Path("CHANGELOG.md")
    content = changelog.read_text()
    
    # Get today's date
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    
    # Replace [Unreleased] with new version
    content = content.replace(
        "## [Unreleased]",
        f"## [Unreleased]\n\n## [{new_version}] - {today}"
    )
    
    changelog.write_text(content)
    print(f"✓ Updated {changelog}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bump version numbers")
    parser.add_argument(
        'bump_type',
        choices=['major', 'minor', 'patch'],
        help='Type of version bump'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    # Read current version
    version_file = Path("src/meshtastic_mqtt_cli/__version__.py")
    content = version_file.read_text()
    match = re.search(r'__version__ = "([^"]+)"', content)
    
    if not match:
        print("Error: Could not find version in __version__.py")
        return 1
    
    current_version = match.group(1)
    new_version = bump_version(current_version, args.bump_type)
    
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    print(f"Bump type: {args.bump_type}")
    
    if args.dry_run:
        print("\n[DRY RUN] No files were modified")
        return 0
    
    print("\nUpdating files...")
    update_version_file(new_version)
    update_changelog(new_version)
    
    print(f"\n✓ Version bumped to {new_version}")
    print("\nNext steps:")
    print(f"  1. Review changes: git diff")
    print(f"  2. Commit changes: git commit -am 'chore: bump version to {new_version}'")
    print(f"  3. Create tag: git tag v{new_version}")
    print(f"  4. Push changes: git push && git push --tags")
    
    return 0


if __name__ == '__main__':
    exit(main())
