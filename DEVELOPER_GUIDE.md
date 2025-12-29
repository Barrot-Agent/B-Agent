# 🛠️ Developer Guide for Barrot-Agent

Welcome to the Barrot-Agent development guide! This document provides essential information for developers working on the Barrot-Agent project.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Node.js (for npm scripts)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Barrot-Agent/Barrot-Agent.git
   cd Barrot-Agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   npm run health
   ```

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
python -m pytest tests/test_manifest_validation.py -v
```

### Test Structure
```
tests/
├── __init__.py
├── test_manifest_validation.py    # Build manifest tests
├── test_workflow_integrity.py     # GitHub workflow tests
└── test_documentation.py          # Documentation tests
```

### Writing Tests
- Tests use `pytest` framework
- Follow existing test patterns
- Ensure tests are isolated and repeatable
- Add tests for new functionality

Example:
```python
def test_my_feature(self):
    """Test description"""
    # Arrange
    expected = "value"
    
    # Act
    result = my_function()
    
    # Assert
    self.assertEqual(result, expected)
```

---

## ✅ Validation

### Validate Build Manifest
```bash
# Validate current manifest
npm run validate

# Or directly:
python scripts/validate_manifest.py
```

### Health Check
```bash
# Run comprehensive health check
npm run health

# Or directly:
python scripts/health_check.py
```

---

## 🔄 Development Workflow

### Before Making Changes

1. **Check system health:**
   ```bash
   npm run health
   ```

2. **Run tests:**
   ```bash
   npm test
   ```

3. **Create feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

### While Developing

1. **Make focused changes**
2. **Write/update tests**
3. **Run tests frequently:**
   ```bash
   npm test
   ```

4. **Validate manifest if changed:**
   ```bash
   npm run validate
   ```

### Before Committing

1. **Run all tests:**
   ```bash
   npm run test:coverage
   ```

2. **Run health check:**
   ```bash
   npm run health
   ```

3. **Check git status:**
   ```bash
   git status
   ```

4. **Stage and commit:**
   ```bash
   git add <files>
   git commit -m "Description of changes"
   ```

### Opening Pull Request

1. **Push to GitHub:**
   ```bash
   git push origin feature/my-feature
   ```

2. **Open PR on GitHub**

3. **Wait for CI/CD checks to pass**

4. **Address review feedback**

---

## 🏗️ Project Structure

```
Barrot-Agent/
├── .github/
│   └── workflows/          # GitHub Actions workflows
│       ├── ci-cd.yml       # Main CI/CD pipeline
│       ├── BBR.yml         # Build Relay workflow
│       └── ...
├── tests/                  # Test suite
│   ├── test_manifest_validation.py
│   ├── test_workflow_integrity.py
│   └── test_documentation.py
├── scripts/                # Utility scripts
│   ├── validate_manifest.py
│   └── health_check.py
├── site/                   # Web dashboard
│   └── index.html
├── memory-bundles/         # Activity logs
├── spells/                 # Agent capabilities
├── build_manifest.yaml     # Build configuration
├── requirements.txt        # Python dependencies
├── package.json            # NPM scripts
└── README.md              # Main documentation
```

---

## 📋 Build Manifest

### Structure
```yaml
build_signature: BNDL-V3-MONETIZATION
timestamp: 2025-12-23T13:25:00Z

modules:
  - prediction_methodologies
  - deployment_integrity
  - ...

rail_status:
  ingestion: active
  deployment: stable
  ...

resources:
  - kaggle
  - github
  ...

capabilities:
  - quantum_entanglement
  - autonomous_gap_filling
  ...
```

### Validation Rules
- `build_signature` must start with "BNDL-"
- `timestamp` must be ISO 8601 format
- `modules` must be a non-empty list
- `rail_status` must be a non-empty dictionary
- Rail status values must be valid: `active`, `stable`, `recursive`, `evolving`, `publishing`, `initializing`, `developing`, `ACTIVE`, `OPERATIONAL`

---

## 🔧 Available NPM Scripts

```bash
# Testing
npm test              # Run all tests
npm run test:coverage # Run tests with coverage report

# Validation
npm run validate      # Validate build manifest
npm run health        # Run health checks

# Linting (placeholder)
npm run lint          # Run linters
```

---

## 📊 CI/CD Pipeline

The repository uses GitHub Actions for CI/CD:

### Workflows

1. **CI/CD Pipeline** (`ci-cd.yml`)
   - Validates manifest
   - Runs tests
   - Checks YAML/JSON syntax
   - Performs security checks
   - Reports build status

2. **Build Relay** (`BBR.yml`)
   - Updates build manifest
   - Publishes dashboard
   - Deploys to GitHub Pages

3. **Ping-Pong** (`Barrot-SHRM-PingPong.yml`)
   - Health monitoring
   - Activity logging

### Trigger Events
- Push to `main` branch
- Pull requests to `main`
- Manual workflow dispatch

---

## 🐛 Debugging

### Test Failures

1. **Run specific test:**
   ```bash
   python -m pytest tests/test_manifest_validation.py::TestManifestValidation::test_build_signature_format -v
   ```

2. **Add debug output:**
   ```python
   import pdb; pdb.set_trace()  # Breakpoint
   ```

3. **Check test output:**
   ```bash
   python -m pytest tests/ -v -s  # Show print statements
   ```

### Manifest Issues

1. **Validate manifest:**
   ```bash
   npm run validate
   ```

2. **Check YAML syntax:**
   ```bash
   python -c "import yaml; print(yaml.safe_load(open('build_manifest.yaml')))"
   ```

### Workflow Issues

1. **Check workflow syntax:**
   ```bash
   python -c "import yaml; yaml.safe_load(open('.github/workflows/ci-cd.yml'))"
   ```

2. **View workflow runs:**
   - Visit: https://github.com/Barrot-Agent/Barrot-Agent/actions

---

## 🔐 Security

### Best Practices
- Never commit secrets or API keys
- Use GitHub Secrets for sensitive data
- Run security checks before committing
- Review dependencies regularly

### Security Checks
The CI/CD pipeline includes basic security scanning:
- Secret pattern detection
- File permission checks
- Dependency vulnerability scanning (future)

---

## 📚 Additional Resources

- [Main README](README.md)
- [Gap Analysis](GAP_ANALYSIS.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Ingestion Manifest](INGESTION_MANIFEST.md)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure all checks pass
5. Open a pull request
6. Respond to review feedback

---

## 💡 Tips

- **Run tests frequently** - Catch issues early
- **Keep changes focused** - Easier to review
- **Write clear commit messages** - Help reviewers understand changes
- **Update documentation** - Keep docs in sync with code
- **Ask questions** - Use issues for clarification

---

## 🆘 Getting Help

- **Issues**: https://github.com/Barrot-Agent/Barrot-Agent/issues
- **Discussions**: https://github.com/Barrot-Agent/Barrot-Agent/discussions
- **Documentation**: Check the docs/ directory

---

**Last Updated**: 2025-12-29  
**Maintained by**: Barrot-Agent Team
