#!/usr/bin/env python3
"""
Script to find links where the link text doesn't match the URL destination.
"""
import re
import os
from pathlib import Path
from urllib.parse import urlparse
import json

def extract_links(content, filepath):
    """Extract all markdown links from content."""
    # Pattern to match [text](url) or [text](url "title")
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = []
    
    for match in re.finditer(link_pattern, content):
        text = match.group(1)
        url = match.group(2)
        # Remove title if present: url "title"
        url = url.split('"')[0].strip()
        line_num = content[:match.start()].count('\n') + 1
        links.append({
            'text': text,
            'url': url,
            'line': line_num,
            'file': filepath
        })
    
    return links

def normalize_path(path):
    """Normalize a path for comparison."""
    # Remove leading/trailing slashes
    path = path.strip('/')
    # Remove .mdx extension if present
    if path.endswith('.mdx'):
        path = path[:-4]
    return path.lower()

def get_url_destination(url):
    """Extract the destination from a URL."""
    # Handle special protocols
    if ':' in url and not url.startswith('http') and not url.startswith('/'):
        # Special protocol like email: or mdc:
        return url
    
    # Handle relative paths
    if url.startswith('/'):
        return normalize_path(url)
    
    # Handle external URLs
    if url.startswith('http'):
        parsed = urlparse(url)
        # Extract path from URL
        path = parsed.path.strip('/')
        if path.endswith('.mdx'):
            path = path[:-4]
        return path.lower() if path else None
    
    # Relative path without leading slash
    return normalize_path(url)

def extract_keywords(text):
    """Extract meaningful keywords from link text."""
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'this', 'that', 'these', 'those', 'guide', 'docs', 'documentation', 'page', 'section'}
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if w not in stop_words and len(w) > 2]

def check_link_match(link):
    """Check if link text matches the URL destination."""
    text = link['text']
    url = link['url']
    
    # Skip certain types of links
    if url.startswith('http') and 'invopop.com' not in url:
        # External links - hard to verify, skip for now
        return None
    
    if url.startswith('mailto:') or url.startswith('email:'):
        # Email links - check if text mentions email
        if 'email' in text.lower() or '@' in text or 'support' in text.lower() or 'contact' in text.lower():
            return True
        return False
    
    if url.startswith('mdc:'):
        # Internal reference - skip for now
        return None
    
    # Get destination from URL
    destination = get_url_destination(url)
    if not destination:
        return None
    
    # Extract keywords from text
    text_keywords = extract_keywords(text)
    
    # Extract keywords from destination
    dest_keywords = extract_keywords(destination.replace('-', ' ').replace('_', ' '))
    
    # Check for obvious mismatches
    # If text mentions something specific but URL points elsewhere
    text_lower = text.lower()
    dest_lower = destination.lower()
    
    # Common mismatch patterns
    mismatches = []
    
    # Check if text mentions a specific feature/app but URL doesn't match
    if 'workflow' in text_lower and 'workflow' not in dest_lower:
        mismatches.append("Text mentions 'workflow' but URL doesn't")
    if 'invoice' in text_lower and 'invoice' not in dest_lower and 'doc' not in dest_lower:
        mismatches.append("Text mentions 'invoice' but URL doesn't")
    if 'supplier' in text_lower and 'supplier' not in dest_lower:
        mismatches.append("Text mentions 'supplier' but URL doesn't")
    if 'api' in text_lower and 'api' not in dest_lower and not url.startswith('/api'):
        mismatches.append("Text mentions 'API' but URL doesn't point to API docs")
    if 'console' in text_lower and 'console' not in dest_lower and not url.startswith('/console'):
        mismatches.append("Text mentions 'console' but URL doesn't point to console docs")
    if 'guide' in text_lower and 'guide' not in dest_lower and not url.startswith('/guides'):
        mismatches.append("Text mentions 'guide' but URL doesn't point to guides")
    
    # Check country/region mismatches
    countries = {
        'spain': 'es', 'portugal': 'pt', 'france': 'fr', 'germany': 'de',
        'italy': 'it', 'poland': 'pl', 'greece': 'gr', 'mexico': 'mx',
        'colombia': 'co', 'brazil': 'br', 'belgium': 'be'
    }
    for country, code in countries.items():
        if country in text_lower and code not in dest_lower and country not in dest_lower:
            # Check if it's a false positive (e.g., "Spain" in text but URL is about something else)
            if any(c in dest_lower for c in ['spain', 'es-', '-es', 'ticketbai', 'facturae', 'verifactu']):
                continue
            mismatches.append(f"Text mentions '{country}' but URL doesn't match")
    
    # Check for specific app/feature names
    apps_features = {
        'peppol': 'peppol',
        'stripe': 'stripe',
        'slack': 'slack',
        'chargebee': 'chargebee',
        'pdf': 'pdf',
        'email': 'email',
        'webhook': 'webhook',
        'authentication': 'authentication',
        'series': 'series',
        'sdi': 'sdi',
        'ksef': 'ksef',
        'sat': 'sat',
        'dian': 'dian',
        'ticketbai': 'ticketbai',
        'facturae': 'facturae',
        'verifactu': 'verifactu',
        'chorus': 'chorus',
        'invoicexpress': 'invoicexpress',
        'at': 'at-portugal',
    }
    
    for term, url_term in apps_features.items():
        if term in text_lower:
            if url_term not in dest_lower and term not in dest_lower:
                # Allow some flexibility for related terms
                if term == 'at' and 'portugal' in dest_lower:
                    continue
                if term == 'chorus' and 'choruspro' in dest_lower:
                    continue
                mismatches.append(f"Text mentions '{term}' but URL doesn't match")
    
    if mismatches:
        return {
            'match': False,
            'reason': '; '.join(mismatches)
        }
    
    # If we have keyword overlap, it's likely a match
    if text_keywords and dest_keywords:
        overlap = set(text_keywords) & set(dest_keywords)
        if len(overlap) >= 2 or (len(overlap) >= 1 and len(text_keywords) <= 3):
            return True
    
    # If destination is in text (allowing for variations)
    if any(word in dest_lower for word in text_keywords if len(word) > 4):
        return True
    
    # If text is very generic, it's probably fine
    generic_terms = ['here', 'this', 'link', 'page', 'docs', 'documentation', 'more', 'learn', 'read', 'see']
    if text_lower in generic_terms or len(text_keywords) == 0:
        return True
    
    # If we can't determine, return None (uncertain)
    return None

def analyze_file(filepath):
    """Analyze a single file for link mismatches."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []
    
    links = extract_links(content, str(filepath))
    issues = []
    
    for link in links:
        result = check_link_match(link)
        if result is False or (isinstance(result, dict) and not result.get('match', True)):
            issues.append({
                'link': link,
                'issue': result.get('reason', 'Link text may not match URL destination') if isinstance(result, dict) else 'Link text may not match URL destination'
            })
    
    return issues

def main():
    """Main function to analyze all MDX files."""
    base_dir = Path('/Users/markmackay/Developer/invopop/docs.invopop.com')
    mdx_files = list(base_dir.rglob('*.mdx'))
    
    all_issues = []
    
    print(f"Analyzing {len(mdx_files)} MDX files...")
    
    for mdx_file in mdx_files:
        issues = analyze_file(mdx_file)
        all_issues.extend(issues)
    
    print(f"\nFound {len(all_issues)} potential link mismatches:\n")
    
    for issue in all_issues:
        link = issue['link']
        print(f"File: {link['file']}")
        print(f"  Line {link['line']}: [{link['text']}]({link['url']})")
        print(f"  Issue: {issue['issue']}")
        print()

if __name__ == '__main__':
    main()

