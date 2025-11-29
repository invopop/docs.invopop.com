#!/usr/bin/env python3
"""
Refined script to find actual link mismatches.
"""
import re
import os
from pathlib import Path

def extract_links(content, filepath):
    """Extract all markdown links from content."""
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = []
    
    for match in re.finditer(link_pattern, content):
        text = match.group(1)
        url = match.group(2)
        url = url.split('"')[0].strip()
        line_num = content[:match.start()].count('\n') + 1
        links.append({
            'text': text,
            'url': url,
            'line': line_num,
            'file': filepath
        })
    
    return links

def check_specific_issues(link):
    """Check for specific known issues."""
    text = link['text'].lower()
    url = link['url']
    issues = []
    
    # Check for /guides/countries/ paths (this directory doesn't exist)
    if '/guides/countries/' in url:
        issues.append(f"Path '/guides/countries/' doesn't exist - should likely be '/guides/'")
    
    # Check for Slack link pointing to email
    if 'slack' in text and url == '/apps/email':
        issues.append("Link text mentions 'Slack' but URL points to '/apps/email' - should be '/apps/slack'")
    
    # Check for typo in anchor
    if url == '#regluation':
        issues.append("Anchor typo: '#regluation' should be '#regulation'")
    
    # Check for workflow text pointing to job API
    if 'workflow' in text and 'jobs' in url and 'workflow' not in url:
        issues.append("Link text mentions 'workflow' but URL is about jobs, not workflows")
    
    # Check for guide text pointing to API reference
    if 'guide' in text and url.startswith('/api-ref/') and 'introduction' not in text.lower():
        issues.append("Link text mentions 'guide' but URL points to API reference")
    
    # Check for invoice text pointing to console redirect without invoice in URL
    if 'invoice' in text and 'console.invopop.com/redirect/workflows' in url and 'empty-invoice' not in url:
        # This might be OK if it's a generic workflow link
        pass
    
    # Check for supplier portal links
    if 'supplier' in text and 'portal' in text and 'at-pt.invopop.com/portal' in url:
        # This is actually correct - the portal is for suppliers
        pass
    
    return issues

def main():
    """Main function to analyze all MDX files."""
    base_dir = Path('/Users/markmackay/Developer/invopop/docs.invopop.com')
    mdx_files = list(base_dir.rglob('*.mdx'))
    
    all_issues = []
    
    print(f"Analyzing {len(mdx_files)} MDX files for link mismatches...\n")
    
    for mdx_file in mdx_files:
        try:
            with open(mdx_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {mdx_file}: {e}")
            continue
        
        links = extract_links(content, str(mdx_file))
        
        for link in links:
            issues = check_specific_issues(link)
            if issues:
                all_issues.append({
                    'link': link,
                    'issues': issues
                })
    
    print(f"Found {len(all_issues)} files with link issues:\n")
    print("=" * 80)
    
    for item in all_issues:
        link = item['link']
        print(f"\nFile: {link['file']}")
        print(f"Line {link['line']}: [{link['text']}]({link['url']})")
        for issue in item['issues']:
            print(f"  ⚠️  {issue}")
        print()

if __name__ == '__main__':
    main()

