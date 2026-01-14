#!/usr/bin/env python3
"""
Clean inline styles from blog post HTML files.
Replaces inline styles with CSS classes for article-content elements.

Usage:
    python3 clean-article-inline-styles.py           # Process all posts
    python3 clean-article-inline-styles.py --dry-run # Preview changes
    python3 clean-article-inline-styles.py --single posts/2025/10/file.html
"""

import os
import re
import argparse
from pathlib import Path

# Base directory
POSTS_DIR = Path(__file__).parent.parent / "posts"

# Replacement patterns (order matters - more specific first)
REPLACEMENTS = [
    # Article container - remove 'container' class
    (
        r'<article class="article-content container">',
        '<article class="article-content">'
    ),

    # Key takeaways box - remove inline styles
    (
        r'<div class="key-takeaways" style="[^"]*">',
        '<div class="key-takeaways">'
    ),
    (
        r'<h3 style="color: white; margin-bottom: 1rem;">Key Takeaways</h3>',
        '<h3>Key Takeaways</h3>'
    ),
    (
        r'<ul style="list-style: none; padding: 0;">',
        '<ul>'
    ),
    (
        r'<li style="margin-bottom: 0\.75rem;">',
        '<li>'
    ),

    # Info box - remove inline styles
    (
        r'<div class="info-box" style="[^"]*">',
        '<div class="info-box">'
    ),

    # Warning/Caution box - convert to warning-box class
    (
        r'<div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 1\.5rem; margin: 1\.5rem 0; border-radius: 0 8px 8px 0;">',
        '<div class="warning-box">'
    ),

    # Success box
    (
        r'<div style="background: #f0fdf4; border-left: 4px solid #22c55e;[^"]*">',
        '<div class="success-box">'
    ),

    # Tables - remove inline styles
    (
        r'<table style="[^"]*">',
        '<table>'
    ),
    (
        r'<thead style="[^"]*">',
        '<thead>'
    ),
    (
        r'<th style="[^"]*">',
        '<th>'
    ),
    (
        r'<td style="[^"]*">',
        '<td>'
    ),
    (
        r'<tr style="[^"]*">',
        '<tr>'
    ),

    # CTA box - remove inline styles
    (
        r'<div class="cta-box" style="[^"]*">',
        '<div class="cta-box">'
    ),
    (
        r'<h3 style="color: white; font-size: 2rem; margin: 0 0 1rem 0;">',
        '<h3>'
    ),
    (
        r'<p style="font-size: 1\.2rem; margin-bottom: 1\.5rem;">',
        '<p>'
    ),
    (
        r'<a href="([^"]*)" class="cta-button" style="[^"]*">',
        r'<a href="\1" class="cta-button">'
    ),

    # Related posts section
    (
        r'<div class="related-posts" style="[^"]*">',
        '<div class="related-posts">'
    ),
    (
        r'<h3 style="font-size: 1\.5rem; margin-bottom: 1\.5rem;">([^<]*)</h3>',
        r'<h3>\1</h3>'
    ),
    (
        r'<div style="display: grid; grid-template-columns: repeat\(auto-fit, minmax\(300px, 1fr\)\); gap: 1\.5rem;">',
        '<div class="related-posts-grid">'
    ),
    (
        r'<div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 1\.5rem;">',
        '<div class="related-post-card">'
    ),
    (
        r'<h4 style="margin: 0 0 0\.5rem 0;"><a href="([^"]*)" style="color: #0ea5e9;">([^<]*)</a></h4>',
        r'<h4><a href="\1">\2</a></h4>'
    ),
    (
        r'<p style="margin: 0; color: #64748b;">',
        '<p>'
    ),

    # Step-by-step sections with inline styles
    (
        r'<div class="step" style="[^"]*">',
        '<div class="step">'
    ),
    (
        r'<span class="step-number" style="[^"]*">',
        '<span class="step-number">'
    ),

    # Related grid with inline styles
    (
        r'<div class="related-grid" style="[^"]*">',
        '<div class="related-grid">'
    ),

    # CTA subtext with inline styles
    (
        r'<p class="cta-subtext" style="[^"]*">',
        '<p class="cta-subtext">'
    ),
]


def clean_html_file(filepath: Path, dry_run: bool = False) -> bool:
    """Clean inline styles from a single HTML file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content

        for pattern, replacement in REPLACEMENTS:
            content = re.sub(pattern, replacement, content)

        if content != original:
            if not dry_run:
                filepath.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Clean inline styles from blog posts')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--single', type=str, help='Process single file')
    args = parser.parse_args()

    print("Cleaning inline styles from blog posts...")
    print("-" * 50)

    if args.single:
        filepath = POSTS_DIR.parent / args.single
        if filepath.exists():
            changed = clean_html_file(filepath, args.dry_run)
            status = "Would update" if args.dry_run else "Updated" if changed else "No changes"
            print(f"  {status}: {args.single}")
        else:
            print(f"  File not found: {args.single}")
        return

    # Process all HTML files in posts directory
    html_files = list(POSTS_DIR.rglob("*.html"))
    updated = 0

    for filepath in sorted(html_files):
        relative_path = filepath.relative_to(POSTS_DIR.parent)
        changed = clean_html_file(filepath, args.dry_run)

        if changed:
            status = "Would update" if args.dry_run else "Updated"
            print(f"  {status}: {relative_path}")
            updated += 1
        else:
            print(f"  No changes: {relative_path}")

    print("-" * 50)
    action = "Would update" if args.dry_run else "Updated"
    print(f"{action} {updated}/{len(html_files)} posts")


if __name__ == "__main__":
    main()
