# Gumroad Integration Documentation

## Overview
This document describes the location and setup of Gumroad-related files for the Barrot-Agent project.

## Current Status
⚠️ **Note**: Gumroad files are not currently present in this repository.

## Recommended File Structure

If you're looking to integrate Gumroad with this project, here's the recommended file structure:

```
Barrot-Agent/
├── gumroad/
│   ├── products/           # Product configurations
│   ├── webhooks/           # Webhook handlers
│   ├── api/                # Gumroad API integration
│   └── config.json         # Gumroad configuration
├── site/
│   ├── checkout.html       # Checkout page
│   └── success.html        # Success page (currently at site/index.html)
└── GUMROAD.md             # This file
```

## Files You Might Be Looking For

### 1. **Product Files** (`gumroad/products/`)
- Product configurations
- Pricing information
- Digital download assets

### 2. **Webhook Handlers** (`gumroad/webhooks/`)
- Payment verification
- License key generation
- Customer notifications

### 3. **API Integration** (`gumroad/api/`)
- Gumroad API client
- Authentication tokens
- API endpoint wrappers

### 4. **Configuration** (`gumroad/config.json`)
- API keys (stored securely)
- Webhook URLs
- Product mappings

## Existing Related Files

The following files already exist in the repository that may be related to a checkout/sales flow:

- **`site/index.html`** - Contains a "Checkout completed" success page
  - Location: `site/index.html`
  - Purpose: Post-checkout success page with redirect to portal

## Setting Up Gumroad Integration

To set up Gumroad integration for this project:

1. **Create the directory structure**:
   ```bash
   mkdir -p gumroad/{products,webhooks,api}
   ```

2. **Add your Gumroad API credentials**:
   - Create `gumroad/config.json` (add to `.gitignore`)
   - Store API keys in environment variables or secure vault

3. **Configure webhooks**:
   - Set up webhook URLs in your Gumroad dashboard
   - Implement webhook handlers in `gumroad/webhooks/`

4. **Add product definitions**:
   - Create product JSON files in `gumroad/products/`
   - Include pricing, descriptions, and download links

## Security Considerations

⚠️ **Important**: Never commit sensitive information to the repository:
- API keys and secrets
- Customer data
- Payment information
- License keys

Use environment variables or a secure secrets manager instead.

## Resources

- [Gumroad API Documentation](https://app.gumroad.com/api)
- [Gumroad Webhooks Guide](https://help.gumroad.com/article/268-webhooks)
- [Gumroad Developer Portal](https://gumroad.com/developer)

## Questions?

If you're looking for specific Gumroad files that should already exist:
1. Check if they're in a different branch
2. Verify with the project maintainer about their location
3. They may need to be created as part of a new integration

---

*Last updated: December 2024*
