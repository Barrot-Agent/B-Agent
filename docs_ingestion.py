#!/usr/bin/env python3
"""
Documentation Ingestion System for Barrot-Agent
Ingests documentation from GitHub, Copilot, ChatGPT/OpenAI, and Snowflake
"""

import os
import json
import time
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class DocParser(HTMLParser):
    """Simple HTML parser to extract text content from documentation pages"""
    
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.in_script = False
        self.in_style = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.in_script = True
        elif tag == 'style':
            self.in_style = True
            
    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False
        elif tag == 'style':
            self.in_style = False
            
    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            text = data.strip()
            if text:
                self.text_content.append(text)
                
    def get_text(self):
        return ' '.join(self.text_content)


class DocsIngestionSystem:
    """Documentation ingestion system for multiple platforms"""
    
    def __init__(self, output_dir='ingested_docs', config_file='docs-ingestion-config.yaml'):
        self.output_dir = output_dir
        self.config_file = config_file
        
        # Try to load configuration from YAML file
        self.config = self._load_config()
        
        # Use configuration if loaded, otherwise use defaults
        if self.config and 'ingestion_config' in self.config:
            self.platforms = self._load_platforms_from_config()
            if self.config['ingestion_config'].get('output', {}).get('directory'):
                self.output_dir = self.config['ingestion_config']['output']['directory']
        else:
            # Fallback to hardcoded defaults if config file not available
            self.platforms = self._get_default_platforms()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _load_config(self):
        """Load configuration from YAML file if available"""
        if not HAS_YAML:
            print("⚠️  PyYAML not installed, using default configuration")
            return None
            
        if not os.path.exists(self.config_file):
            print(f"⚠️  Config file {self.config_file} not found, using default configuration")
            return None
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  Error loading config file: {e}, using default configuration")
            return None
    
    def _load_platforms_from_config(self):
        """Load platform configurations from the YAML config"""
        platforms = {}
        config_platforms = self.config['ingestion_config'].get('platforms', {})
        
        for key, platform_config in config_platforms.items():
            if platform_config.get('enabled', True):
                platforms[key] = {
                    'name': platform_config.get('name', key),
                    'base_url': platform_config.get('base_url', ''),
                    'key_paths': platform_config.get('key_sections', [])
                }
        
        return platforms
    
    def _get_default_platforms(self):
        """Return default platform configuration if config file not available"""
        return {
            'github': {
                'name': 'GitHub Docs',
                'base_url': 'https://docs.github.com',
                'key_paths': [
                    '/en/get-started',
                    '/en/actions',
                    '/en/rest',
                    '/en/graphql',
                    '/en/copilot'
                ]
            },
            'copilot': {
                'name': 'GitHub Copilot Docs',
                'base_url': 'https://docs.github.com',
                'key_paths': [
                    '/en/copilot',
                    '/en/copilot/using-github-copilot',
                    '/en/copilot/configuring-github-copilot',
                    '/en/copilot/managing-copilot'
                ]
            },
            'copilot_cookbook': {
                'name': 'GitHub Copilot Cookbook',
                'base_url': 'https://docs.github.com',
                'key_paths': [
                    '/en/copilot/example-prompts-for-github-copilot-chat',
                    '/en/copilot/using-github-copilot/getting-code-suggestions-in-your-ide-with-github-copilot',
                    '/en/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide'
                ]
            },
            'claude_skills': {
                'name': 'Claude Skills Documentation',
                'base_url': 'https://support.anthropic.com',
                'key_paths': [
                    '/en/collections',
                    '/en/articles'
                ]
            },
            'openai': {
                'name': 'OpenAI/ChatGPT Docs',
                'base_url': 'https://platform.openai.com',
                'key_paths': [
                    '/docs/introduction',
                    '/docs/quickstart',
                    '/docs/guides',
                    '/docs/api-reference',
                    '/docs/models'
                ]
            },
            'snowflake': {
                'name': 'Snowflake Docs',
                'base_url': 'https://docs.snowflake.com',
                'key_paths': [
                    '/en/user-guide',
                    '/en/sql-reference',
                    '/en/developer-guide',
                    '/en/data-loading',
                    '/en/user-guide/ml-functions'
                ]
            }
        }
        
    def fetch_page(self, url, max_retries=3):
        """Fetch a single documentation page with retry logic"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Barrot-Agent/1.0; Documentation Ingestion Bot)'
        }
        
        for attempt in range(max_retries):
            try:
                request = Request(url, headers=headers)
                with urlopen(request, timeout=10) as response:
                    if response.status == 200:
                        content = response.read().decode('utf-8')
                        return content
                    else:
                        print(f"  ⚠️  HTTP {response.status} for {url}")
            except HTTPError as e:
                print(f"  ⚠️  HTTP Error {e.code} for {url}")
                if e.code == 404:
                    return None  # Don't retry 404s
            except URLError as e:
                print(f"  ⚠️  URL Error for {url}: {e.reason}")
            except Exception as e:
                print(f"  ⚠️  Error fetching {url}: {str(e)}")
                
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                
        return None
        
    def parse_content(self, html_content):
        """Parse HTML content and extract text"""
        parser = DocParser()
        try:
            parser.feed(html_content)
            return parser.get_text()
        except Exception as e:
            print(f"  ⚠️  Error parsing content: {str(e)}")
            return ""
            
    def ingest_platform(self, platform_key):
        """Ingest documentation from a single platform"""
        platform = self.platforms[platform_key]
        print(f"\n📚 Ingesting {platform['name']}...")
        
        results = {
            'platform': platform['name'],
            'platform_key': platform_key,
            'base_url': platform['base_url'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'pages': []
        }
        
        for path in platform['key_paths']:
            url = platform['base_url'] + path
            print(f"  📄 Fetching: {url}")
            
            html_content = self.fetch_page(url)
            if html_content:
                text_content = self.parse_content(html_content)
                
                page_result = {
                    'url': url,
                    'path': path,
                    'content_length': len(text_content),
                    'preview': text_content[:200] + '...' if len(text_content) > 200 else text_content,
                    'fetched_at': datetime.utcnow().isoformat() + 'Z',
                    'status': 'success'
                }
                results['pages'].append(page_result)
                
                # Save individual page content
                filename = f"{platform_key}_{path.replace('/', '_')}.txt"
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"URL: {url}\n")
                    f.write(f"Fetched: {page_result['fetched_at']}\n")
                    f.write(f"{'='*80}\n\n")
                    f.write(text_content)
                    
                print(f"    ✅ Saved {len(text_content)} characters")
            else:
                page_result = {
                    'url': url,
                    'path': path,
                    'status': 'failed',
                    'fetched_at': datetime.utcnow().isoformat() + 'Z'
                }
                results['pages'].append(page_result)
                print(f"    ❌ Failed to fetch")
                
            # Be respectful with rate limiting
            time.sleep(1)
            
        # Save platform summary
        summary_file = os.path.join(self.output_dir, f"{platform_key}_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        success_count = sum(1 for p in results['pages'] if p['status'] == 'success')
        print(f"  ✅ Completed: {success_count}/{len(results['pages'])} pages successfully ingested")
        
        return results
        
    def ingest_all(self):
        """Ingest documentation from all platforms"""
        print("🚀 Starting Documentation Ingestion System")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🕐 Started at: {datetime.utcnow().isoformat()}Z")
        
        all_results = {
            'ingestion_run': {
                'started_at': datetime.utcnow().isoformat() + 'Z',
                'platforms': {}
            }
        }
        
        for platform_key in self.platforms.keys():
            try:
                results = self.ingest_platform(platform_key)
                all_results['ingestion_run']['platforms'][platform_key] = {
                    'status': 'completed',
                    'pages_ingested': sum(1 for p in results['pages'] if p['status'] == 'success'),
                    'total_pages': len(results['pages'])
                }
            except Exception as e:
                print(f"\n❌ Error ingesting {platform_key}: {str(e)}")
                all_results['ingestion_run']['platforms'][platform_key] = {
                    'status': 'failed',
                    'error': str(e)
                }
                
        all_results['ingestion_run']['completed_at'] = datetime.utcnow().isoformat() + 'Z'
        
        # Save overall summary
        summary_file = os.path.join(self.output_dir, 'ingestion_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
            
        print(f"\n✨ Ingestion completed!")
        print(f"📊 Summary saved to: {summary_file}")
        
        return all_results


def main():
    """Main entry point for the documentation ingestion system"""
    ingestion_system = DocsIngestionSystem()
    results = ingestion_system.ingest_all()
    
    # Print summary
    print("\n" + "="*80)
    print("📈 INGESTION SUMMARY")
    print("="*80)
    for platform, data in results['ingestion_run']['platforms'].items():
        if data['status'] == 'completed':
            print(f"  {platform}: {data['pages_ingested']}/{data['total_pages']} pages")
        else:
            print(f"  {platform}: FAILED - {data.get('error', 'Unknown error')}")
    print("="*80)


if __name__ == '__main__':
    main()
