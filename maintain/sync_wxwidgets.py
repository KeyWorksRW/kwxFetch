#!/usr/bin/env python3
"""
Sync wxWidgets source to kwxFetch with filtering rules.

This script copies files from a wxWidgets source (local clone or extracted archive)
to the kwxFetch destination, applying filtering rules to exclude unnecessary files.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Set

# Folders ignored anywhere in path
IGNORE_FOLDER_NAMES: Set[str] = {
    "android", "benchmarks", "bin", "bld", "CMakeFiles", "demos", "distrib",
    "doc", "docs", "examples", "interface", "iphone", "lib", "locale", "m4",
    "man", "misc", "port", "projects", "protocols", "qt", "samples", "scripts",
    "stb", "testdata", "test", "tests",
}

# Specific paths relative to root (use forward slashes)
IGNORE_SPECIFIC_PATHS: Set[str] = {
    "autom4te.cache", "bld", "buildgtk", "demos", "distrib", "docs",
    "interface", "lib", "locale", "misc", "samples", "tests", "msw_build",
    "gcc_build", "3rdparty/catch", "3rdparty/expat/testdata",
    "3rdparty/lunasvg/subprojects", "3rdparty/nanosvg/example",
    "build/bakefiles", "build/libs", "build/msw/gcc_mswudll", "build/utils",
    "src/zlib/amiga", "src/png/ci", "src/png/contrib",
    "src/stc/lexilla/src/Lexilla/Lexilla.xcodeproj",
    "src/stc/scintilla/cocoa/ScintillaTest", "src/zlib/contrib",
    "src/zlib/msdos", "src/zlib/nintendods", "src/zlib/old", "src/zlib/os400",
    "src/zlib/projects", "src/zlib/qnx", "utils/helpview", "utils/hhp2cached",
    "utils/ifacecheck", "utils/screenshotgen",
}

# Files to ignore by name (case-sensitive)
IGNORE_FILES: Set[str] = {
    ".git-blame-ignore-revs", "Makefile.in", "mkinstalldirs", "regen",
    "README-GIT.md", "CONTRIBUTING", "tgzsrc", "makefile", "ScintRes.rc",
    ".ninja_deps", ".ninja_log", ".mailmap", ".bakefile_gen.state",
    "README.md", "smiley.png", "compile", "depcomp", "install-sh", "missing",
}

# Extensions to ignore (lowercase, with dot)
IGNORE_EXTENSIONS: Set[str] = {
    ".gcc", ".m4", ".mk", ".mms", ".pl", ".py", ".sh", ".sln", ".yaml", ".yml",
    ".am", ".ansi", ".b32", ".b64", ".bat", ".bcc", ".bkl", ".bcb", ".bor",
    ".build", ".c32", ".com", ".d32", ".def", ".dist", ".dj", ".filters",
    ".generic", ".gitattributes", ".gitignore", ".guess", ".hgeol",
    ".hgignore", ".hgtags", ".list", ".in", ".mac", ".mak", ".map", ".manx",
    ".mc6", ".msc", ".ninja", ".opt", ".pdf", ".plist", ".props", ".pro",
    ".properties", ".ruleset", ".sas", ".st", ".sub", ".suppress", ".tmpl",
    ".txt", ".unix", ".v16", ".vc", ".vc6", ".vc16", ".vcproj", ".vcxproj",
    ".vs", ".vms", ".wat", ".x32", ".xc",
    # wxLua
    ".lua", ".i",
    # Perl/wxPerl
    ".xsp", ".t", ".pm", ".xs",
}

# Files that MUST be included even if rules would exclude them (relative paths or filenames)
EXCEPTION_FILES: Set[str] = {
    "build/bakefiles/version.bkl",
    "CMakeLists.txt",
}

# Paths where folder name exclusions should NOT apply
# - cmake config needs lib/locale subdirs
# - submodule source directories have lib folders with actual source code
ALLOW_SPECIFIC_PATHS: Set[str] = {
    "build/cmake/lib",
    "build/cmake/locale",
    "src/expat/expat/lib",
    "src/jpeg",
    "src/png",
    "src/tiff",
    "src/zlib",
    "3rdparty/libwebp",
    "3rdparty/pcre",
    "3rdparty/lunasvg",
    "3rdparty/nanosvg",
}

# File patterns in specific directories that should be included despite extension rules
# Format: (path_prefix, extension)
EXCEPTION_EXTENSIONS: Set[tuple] = {
    ("build/cmake", ".in"),
    ("3rdparty/libwebp", ".in"),
    ("3rdparty/libwebp", ".ac"),  # configure.ac needed for cmake
    ("3rdparty/libwebp", ".am"),  # Makefile.am used to determine source files
    ("3rdparty/pcre", ".in"),
    ("src/expat", ".in"),
    ("src/jpeg", ".in"),
    ("src/png", ".in"),
    ("src/tiff", ".in"),
    ("src/zlib", ".in"),
}

# Specific .in files at the root level that must be included
ROOT_EXCEPTION_FILES: Set[str] = {
    "wx-config.in",
    "version-script.in",
    "wx-config-inplace.in",
}

# Extensions allowed for new files (files that don't exist in dest)
ALLOWED_NEW_EXTENSIONS: Set[str] = {
    ".cpp", ".cxx", ".cc", ".c", ".h", ".hpp", ".hxx", ".hh", ".mm", ".cmake",
    ".inc",  # Include files
    ".xpm",  # X pixmap images (used by wxWidgets)
}


def normalize_path(path: str) -> str:
    """Normalize path separators to forward slashes."""
    return path.replace("\\", "/")


def is_in_allowed_path(rel_path: str) -> bool:
    """Check if path is within an explicitly allowed path."""
    return any(rel_path == p or rel_path.startswith(p + "/") for p in ALLOW_SPECIFIC_PATHS)


def is_in_ignored_folder(rel_path: str) -> bool:
    """Check if path contains an ignored folder name."""
    # Skip check if path is explicitly allowed
    if is_in_allowed_path(rel_path):
        return False
    parts = rel_path.split("/")
    return any(part in IGNORE_FOLDER_NAMES for part in parts[:-1])


def is_ignored_specific_path(rel_path: str) -> bool:
    """Check if path starts with an ignored specific path."""
    return any(rel_path == p or rel_path.startswith(p + "/") for p in IGNORE_SPECIFIC_PATHS)


def is_exception_file(rel_path: str) -> bool:
    """Check if file is in the exception list."""
    # Check exact match
    if rel_path in EXCEPTION_FILES:
        return True
    # Check filename-only matches (for files like "CMakeLists.txt" anywhere)
    filename = os.path.basename(rel_path)
    return filename in EXCEPTION_FILES


def has_exception_extension(rel_path: str) -> bool:
    """Check if file has an exception extension for its path."""
    ext = os.path.splitext(rel_path)[1].lower()
    for path_prefix, exc_ext in EXCEPTION_EXTENSIONS:
        if rel_path.startswith(path_prefix + "/") and ext == exc_ext:
            return True
    return False


def should_include_file(rel_path: str, dest_exists: bool) -> tuple[bool, str]:
    """
    Determine if a file should be included.

    Returns:
        (should_include, reason) tuple
    """
    rel_path = normalize_path(rel_path)
    filename = os.path.basename(rel_path)
    ext = os.path.splitext(filename)[1].lower()

    # Check exact-path exception files FIRST (they override all exclusions)
    if rel_path in EXCEPTION_FILES:
        return True, "exception (exact path)"

    # Check root-level .in exception files
    if filename in ROOT_EXCEPTION_FILES and "/" not in rel_path:
        return True, "root exception file"

    # Check ignored folders (but respect ALLOW_SPECIFIC_PATHS)
    if is_in_ignored_folder(rel_path):
        return False, f"ignored folder in path"

    # Check specific ignored paths
    if is_ignored_specific_path(rel_path):
        return False, f"ignored specific path"

    # Exception files by filename (like CMakeLists.txt anywhere)
    if filename in EXCEPTION_FILES:
        return True, "exception"

    # Check ignored files by name (before extension exceptions)
    if filename in IGNORE_FILES:
        return False, f"ignored file name"

    # Check for exception extensions (e.g., .in files in build/cmake)
    if has_exception_extension(rel_path):
        return True, "exception extension"

    # Check ignored extensions
    if ext in IGNORE_EXTENSIONS:
        return False, f"ignored extension {ext}"

    # For new files, check allowed extensions
    if not dest_exists:
        if ext not in ALLOWED_NEW_EXTENSIONS:
            return False, f"new file with non-allowed extension {ext}"

    return True, "passed all filters"


def files_are_identical(src_path: Path, dest_path: Path) -> bool:
    """Compare file contents."""
    try:
        return src_path.read_bytes() == dest_path.read_bytes()
    except (IOError, OSError):
        return False


def sync_files(source: Path, dest: Path, dry_run: bool = False, verbose: bool = False) -> dict:
    """
    Sync files from source to destination with filtering.

    Returns:
        Dict with counts: added, updated, skipped, unchanged
    """
    stats = {"added": 0, "updated": 0, "skipped": 0, "unchanged": 0}
    changes = {"added": [], "updated": [], "skipped": []}

    source = source.resolve()
    dest = dest.resolve()

    if not source.exists():
        print(f"Error: Source path does not exist: {source}", file=sys.stderr)
        sys.exit(1)

    print(f"Syncing from: {source}")
    print(f"Syncing to:   {dest}")
    print(f"Dry run:      {dry_run}")
    print()

    for src_file in source.rglob("*"):
        if not src_file.is_file():
            continue

        # Skip .git directory
        try:
            rel_path = src_file.relative_to(source)
        except ValueError:
            continue

        rel_path_str = normalize_path(str(rel_path))

        if rel_path_str.startswith(".git/") or rel_path_str == ".git":
            continue

        dest_file = dest / rel_path
        dest_exists = dest_file.exists()

        should_include, reason = should_include_file(rel_path_str, dest_exists)

        if not should_include:
            stats["skipped"] += 1
            if verbose:
                changes["skipped"].append(f"{rel_path_str} ({reason})")
            continue

        if dest_exists:
            if files_are_identical(src_file, dest_file):
                stats["unchanged"] += 1
                continue
            else:
                stats["updated"] += 1
                changes["updated"].append(rel_path_str)
                if not dry_run:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    dest_file.write_bytes(src_file.read_bytes())
        else:
            stats["added"] += 1
            changes["added"].append(rel_path_str)
            if not dry_run:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_bytes(src_file.read_bytes())

    # Print summary
    print("=" * 60)
    print("Summary:")
    print(f"  Added:     {stats['added']}")
    print(f"  Updated:   {stats['updated']}")
    print(f"  Unchanged: {stats['unchanged']}")
    print(f"  Skipped:   {stats['skipped']}")
    print()

    if changes["added"]:
        print("Added files:")
        for f in sorted(changes["added"])[:50]:
            print(f"  + {f}")
        if len(changes["added"]) > 50:
            print(f"  ... and {len(changes['added']) - 50} more")
        print()

    if changes["updated"]:
        print("Updated files:")
        for f in sorted(changes["updated"])[:50]:
            print(f"  ~ {f}")
        if len(changes["updated"]) > 50:
            print(f"  ... and {len(changes['updated']) - 50} more")
        print()

    if verbose and changes["skipped"]:
        print("Skipped files (first 100):")
        for f in sorted(changes["skipped"])[:100]:
            print(f"  - {f}")
        if len(changes["skipped"]) > 100:
            print(f"  ... and {len(changes['skipped']) - 100} more")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Sync wxWidgets source to kwxFetch with filtering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be synced
  python sync_wxwidgets.py --source C:/tmp/wxWidgets --dest . --dry-run

  # Actual sync
  python sync_wxwidgets.py --source C:/tmp/wxWidgets --dest .

  # Verbose output (show skipped files)
  python sync_wxwidgets.py --source /tmp/wxWidgets --dest . --verbose
"""
    )

    parser.add_argument(
        "--source", "-s",
        required=True,
        help="Path to wxWidgets source (local clone or extracted archive)"
    )
    parser.add_argument(
        "--dest", "-d",
        required=True,
        help="Destination path (kwxFetch root)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show skipped files"
    )

    args = parser.parse_args()

    source = Path(args.source)
    dest = Path(args.dest)

    sync_files(source, dest, dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()
