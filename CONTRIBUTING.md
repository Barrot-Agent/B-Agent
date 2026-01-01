# Contributing to Barrot

Thank you for your interest in contributing to Barrot! This document provides guidelines and instructions for contributing.

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Submitting Changes](#submitting-changes)
8. [Reporting Bugs](#reporting-bugs)
9. [Feature Requests](#feature-requests)

## Code of Conduct

Please be respectful and considerate in all interactions. We aim to maintain a welcoming and inclusive community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/your-username/Barrot-Agent.git
   cd Barrot-Agent
   ```
3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/Barrot-Agent/Barrot-Agent.git
   ```

## Development Setup

### Prerequisites
- Node.js 18 or higher
- npm or yarn
- Git
- Modern web browser

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open browser**
   Navigate to `http://localhost:3000`

## Making Changes

### Branch Naming Convention

Use descriptive branch names:
- `feature/add-new-feature`
- `fix/bug-description`
- `docs/update-readme`
- `refactor/improve-performance`

### Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### Keep Your Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

## Coding Standards

### JavaScript

- Use ES6+ features
- Use `const` for constants, `let` for variables
- Use arrow functions where appropriate
- Use template literals for string interpolation
- Add comments for complex logic
- Use meaningful variable and function names

**Example:**
```javascript
// Good
const getUserData = async (userId) => {
  try {
    const response = await fetch(`/api/users/${userId}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching user:', error);
    return null;
  }
};

// Avoid
function getData(id) {
  var x = fetch('/api/users/' + id);
  return x;
}
```

### CSS

- Use CSS custom properties (variables)
- Follow BEM naming convention for classes
- Keep selectors simple and performant
- Use flexbox/grid for layouts
- Mobile-first responsive design

**Example:**
```css
/* Good */
.feature-card {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-md);
}

.feature-card__title {
  font-size: var(--font-size-lg);
  color: var(--primary-color);
}

/* Avoid */
.fc {
  display: block;
}

div.card > h3 {
  font-size: 24px;
}
```

### HTML

- Use semantic HTML5 elements
- Include alt text for images
- Use ARIA labels for accessibility
- Keep structure clean and readable

**Example:**
```html
<!-- Good -->
<section class="features" aria-label="Features">
  <h2>Our Features</h2>
  <article class="feature-card">
    <img src="icon.png" alt="Streaming feature icon">
    <h3>Live Streaming</h3>
  </article>
</section>

<!-- Avoid -->
<div class="section">
  <div class="title">Features</div>
  <div class="card">
    <img src="icon.png">
    <div>Streaming</div>
  </div>
</div>
```

### Backend (Node.js)

- Use async/await instead of callbacks
- Add proper error handling
- Use environment variables for configuration
- Add input validation
- Write clear API documentation

**Example:**
```javascript
// Good
app.post('/api/users', async (req, res) => {
  try {
    const { username, email } = req.body;
    
    if (!username || !email) {
      return res.status(400).json({ 
        error: 'Username and email are required' 
      });
    }
    
    const user = await createUser({ username, email });
    res.status(201).json(user);
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

## Testing

### Before Submitting

- [ ] Test all features you modified
- [ ] Test on multiple browsers
- [ ] Test responsive design
- [ ] Check console for errors
- [ ] Run linter (if available)
- [ ] Test API endpoints
- [ ] Verify no breaking changes

### Running Tests

```bash
npm test
```

### Manual Testing

Follow the [Testing Guide](TESTING.md) to manually test features.

## Submitting Changes

### Commit Messages

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "Add WebSocket support for real-time chat"
git commit -m "Fix streaming quality selector bug"
git commit -m "Update README with installation instructions"

# Avoid
git commit -m "fix"
git commit -m "update"
git commit -m "changes"
```

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat: Add video quality selection for streaming

- Add quality selector dropdown (480p, 720p, 1080p)
- Update WebRTC constraints based on selection
- Persist user's quality preference
- Add UI tests for quality selector

Closes #123
```

### Creating a Pull Request

1. **Push your changes**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub

3. **Fill in the PR template**
   - Describe your changes
   - Reference related issues
   - Add screenshots if applicable
   - List testing performed

4. **Wait for review**
   - Address reviewer comments
   - Make requested changes
   - Push updates to the same branch

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Changes Made
- Added feature X
- Fixed bug Y
- Updated documentation Z

## Testing
- [ ] Tested locally
- [ ] Tested on Chrome
- [ ] Tested on Firefox
- [ ] Tested on mobile
- [ ] Added/updated tests

## Screenshots
(if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-reviewed my code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests
- [ ] All tests pass
```

## Reporting Bugs

### Before Reporting

1. Check if bug is already reported
2. Try to reproduce the bug
3. Check if it's fixed in latest version

### Bug Report Template

```markdown
**Describe the Bug**
Clear description of the bug

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- Browser: [Chrome 120.0]
- OS: [Windows 11]
- Version: [1.0.0]

**Additional Context**
Any other relevant information

**Console Errors**
```
Error messages here
```
```

## Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Problem it Solves**
What problem does this solve?

**Proposed Solution**
How would you implement it?

**Alternatives Considered**
Other solutions you've thought about

**Additional Context**
Mockups, examples, etc.
```

## Areas for Contribution

### High Priority
- WebSocket support for real-time chat
- User authentication system
- Recording file management
- Performance optimizations
- Accessibility improvements

### Good First Issues
- UI improvements
- Documentation updates
- Bug fixes
- Test coverage
- Code comments

### Advanced Features
- WebRTC signaling server
- Advanced audio effects
- 3D model import/export
- Multi-user streaming
- Cloud storage integration

## Development Tips

### Debugging
- Use browser DevTools
- Check Network tab for API calls
- Use React DevTools (if applicable)
- Console.log strategically
- Use debugger statements

### Performance
- Minimize DOM manipulations
- Use requestAnimationFrame for animations
- Lazy load resources
- Optimize images
- Profile with Chrome DevTools

### Accessibility
- Test with keyboard only
- Use semantic HTML
- Add ARIA labels
- Ensure color contrast
- Test with screen readers

## Getting Help

- **Documentation**: Check README and other docs
- **Issues**: Search existing issues
- **Discussions**: Start a GitHub discussion
- **Contact**: Email maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project website (when available)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (ISC License).

---

Thank you for contributing to Barrot! 🎉
