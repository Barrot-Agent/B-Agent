# 📚 Documentation Ingestion System

Automated documentation ingestion system for Barrot-Agent that collects and processes documentation from GitHub, Copilot, ChatGPT/OpenAI, Snowflake, and Claude.

## 🎯 Overview

This system automatically fetches, parses, and stores documentation from multiple platforms to enhance Barrot-Agent's knowledge base and capabilities.

## 🚀 Supported Platforms

### 1. **GitHub Docs** (`https://docs.github.com`)
- Getting Started guides
- GitHub Actions
- REST API reference
- GraphQL API reference
- Code Security
- Pull Requests

### 2. **GitHub Copilot Docs** (`https://docs.github.com/copilot`)
- Using GitHub Copilot
- Configuration guides
- Management and administration
- Troubleshooting

### 3. **GitHub Copilot Cookbook** (`https://docs.github.com/copilot`)
- Example prompts for GitHub Copilot Chat
- Getting code suggestions in your IDE
- Asking questions in your IDE
- Practical recipes and patterns

### 4. **Claude Skills Documentation** (`https://support.anthropic.com`)
- Educational platform documentation
- Collections and articles
- Best practices for educational AI usage

### 5. **OpenAI/ChatGPT Docs** (`https://platform.openai.com/docs`)
- API Introduction
- Quickstart guides
- API Reference
- Models documentation
- Prompt engineering
- Assistants API

### 6. **Snowflake Docs** (`https://docs.snowflake.com`)
- User Guide
- SQL Reference
- Developer Guide
- Data Loading
- ML Functions
- Performance Optimization

## 📦 Installation

No additional dependencies required! The system uses Python's standard library only:
- `urllib` for HTTP requests
- `html.parser` for HTML parsing
- `json` for data serialization

## 🎮 Usage

### Basic Usage

Run the documentation ingestion system:

```bash
python3 docs_ingestion.py
```

This will:
1. Create an `ingested_docs/` directory
2. Fetch documentation from all six platforms
3. Save individual page content as text files
4. Generate JSON summaries for each platform
5. Create an overall ingestion summary

### Output Structure

```
ingested_docs/
├── ingestion_summary.json          # Overall ingestion report
├── github_summary.json             # GitHub docs summary
├── copilot_summary.json            # Copilot docs summary
├── openai_summary.json             # OpenAI docs summary
├── snowflake_summary.json          # Snowflake docs summary
├── github_en_get-started.txt       # Individual page content
├── copilot_en_copilot.txt
└── ... (more documentation files)
```

## ⚙️ Configuration

Edit `docs-ingestion-config.yaml` to customize:

- **Output settings**: Directory, format, metadata inclusion
- **Platform settings**: Enable/disable platforms, update frequency
- **Rate limiting**: Requests per minute, delays
- **Processing options**: Code block extraction, link extraction

## 🔄 Ingestion Process

1. **Fetch**: HTTP requests to documentation URLs
2. **Parse**: Extract text content from HTML
3. **Store**: Save as text files with metadata
4. **Summarize**: Generate JSON reports
5. **Integrate**: Update INGESTION_MANIFEST.md

## 📊 Features

### Automated Updates
- Periodic re-ingestion to capture documentation updates
- Timestamp tracking for freshness monitoring

### Rate Limiting
- Respectful request pacing (1 second between requests)
- Exponential backoff on failures
- Maximum retry attempts

### Error Handling
- Graceful handling of HTTP errors
- Retry logic with exponential backoff
- Detailed error logging

### Content Processing
- HTML parsing and text extraction
- Removal of scripts and styles
- Whitespace normalization

## 🔗 Integration with INGESTION_MANIFEST.md

The system integrates with the existing `INGESTION_MANIFEST.md` file:
- Documentation sources are tracked in the manifest
- Ingestion timestamps are recorded
- Status updates are logged

## 📈 Monitoring

View ingestion results:

```bash
# View overall summary
cat ingested_docs/ingestion_summary.json

# View platform-specific summary
cat ingested_docs/github_summary.json

# View actual documentation content
cat ingested_docs/github_en_get-started.txt
```

## 🛠️ Customization

### Adding New Documentation Sources

Edit `docs_ingestion.py` and add to the `platforms` dictionary:

```python
'new_platform': {
    'name': 'New Platform Docs',
    'base_url': 'https://docs.example.com',
    'key_paths': [
        '/path/to/docs',
        '/another/path'
    ]
}
```

### Modifying Fetch Behavior

Adjust these parameters in the `DocsIngestionSystem` class:
- `max_retries`: Number of retry attempts (default: 3)
- `timeout`: Request timeout in seconds (default: 10)
- `User-Agent`: HTTP User-Agent header

## 🔐 Best Practices

1. **Respect rate limits**: The system includes built-in delays
2. **Monitor bandwidth**: Large documentation sites can consume significant bandwidth
3. **Update regularly**: Run periodically to keep documentation fresh
4. **Check summaries**: Review JSON summaries for failed fetches

## 📝 Notes

- All ingested content is stored locally in `ingested_docs/`
- The system is designed to be respectful of documentation servers
- Failed fetches are logged but don't stop the ingestion process
- Each platform can be ingested independently

## 🚨 Troubleshooting

### Connection Errors
- Check internet connectivity
- Verify documentation URLs are accessible
- Review firewall settings

### Parse Errors
- Some documentation sites use complex JavaScript rendering
- Static HTML pages work best
- Consider using API endpoints if available

### Rate Limiting
- Increase delays in configuration
- Reduce concurrent requests
- Spread ingestion across longer time periods

## 🎯 Next Steps

- Implement incremental updates (only fetch changed pages)
- Add support for documentation search/indexing
- Create visualization of documentation coverage
- Add support for PDF documentation sources
- Implement semantic analysis of ingested content

## 📄 License

Part of the Barrot-Agent project. See main repository for license information.
