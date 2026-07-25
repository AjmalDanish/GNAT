# GitHub Repository Setup Guide

This guide will help you set up the GNAT GitHub repository professionally with all necessary configurations.

---

## Prerequisites

Before proceeding, you need:

1. **GitHub Account**: Create one at https://github.com if you don't have one
2. **GitHub Personal Access Token (PAT)**: For authentication with 2FA enabled

### Creating a GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Name it: `GNAT Development Token`
4. Select scopes (check these boxes):
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:org` (Full control of organizations)
   - `admin:public_key` (Full control of public keys)
   - `admin:repo_hook` (Full control of repository hooks)
   - `admin:org_hook` (Full control of organization hooks)
   - `user` (Update user profile data)
5. Click **Generate token**
6. **Copy the token immediately** - you won't see it again!

---

## Step 1: Create the GitHub Repository

### Option A: Using GitHub CLI (Recommended)

1. Install GitHub CLI: https://cli.github.com/
2. Authenticate:
   ```bash
   gh auth login
   ```
   - Select `GitHub.com`
   - Choose `HTTPS`
   - Select `Login with a web browser` OR paste your token

3. Create repository:
   ```bash
   cd D:/project/Global-Network-Anomaly-Tracker-Blueprint
   gh repo create GNAT --public --description "Global Network Anomaly Tracker - AI-powered network traffic analysis using Graph Neural Networks" --source=. --remote=origin --push
   ```

### Option B: Using Web Interface

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name**: `GNAT`
   - **Description**: `Global Network Anomaly Tracker - AI-powered network traffic analysis using Graph Neural Networks`
   - **Visibility**: Public
   - **Initialize with**: ✗ (leave unchecked)
3. Click **Create repository**

---

## Step 2: Push Local Repository to GitHub

After creating the repository on GitHub, run these commands:

```bash
cd D:/project/Global-Network-Anomaly-Tracker-Blueprint

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://YOUR_USERNAME@github.com/YOUR_USERNAME/GNAT.git

# Push main branch
git push -u origin main

# Push develop branch
git push -u origin develop
```

---

## Step 3: Configure Repository Settings

### 3.1 Branch Protection Rules

1. Go to: Settings → Branches
2. Click **Add branch protection rule**
3. Add rules:

#### For `main` branch:
- **Branch name pattern**: `main`
- **Require status checks to pass before merging**: ✅
- **Require branches to be up to date before merging**: ✅
- **Require pull request reviews before merging**: ✅
  - Required approving reviews: 1
  - Dismiss stale PR approvals when new commits are pushed: ✅
- **Require conversation resolution before merging**: ✅
- **Require linear history**: ✅
- **Include administrators**: ✅

#### For `develop` branch:
- **Branch name pattern**: `develop`
- **Require status checks to pass before merging**: ✅
- **Require pull request reviews before merging**: ✅
  - Required approving reviews: 1
- **Include administrators**: ✅

### 3.2 Repository Labels

Go to Settings → Labels → Create these labels:

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | `d73a4a` | Something isn't working |
| `feature` | `a2eeef` | New feature or request |
| `enhancement` | `84b6eb` | Improving existing feature |
| `documentation` | `0075ca` | Improvements to documentation |
| `testing` | `fbca04` | Testing and QA |
| `security` | `02d7e1` | Security related |
| `performance` | `5319e7` | Performance improvements |
| `ai` | `7057ff` | AI/ML related |
| `backend` | `0066cc` | Backend development |
| `frontend` | `0e8a16` | Frontend development |
| `database` | `e6e6e6` | Database related |
| `deployment` | `bfd4f2` | Deployment and DevOps |
| `refactor` | `fbca04` | Code refactoring |
| `critical` | `b60205` | Critical priority |
| `high` | `d93f0b` | High priority |
| `medium` | `fbca04` | Medium priority |
| `low` | `0e8a16` | Low priority |

### 3.3 Repository Topics

Go to: Settings → About → Add Topics

```
django, graph-neural-networks, network-security, anomaly-detection, pytorch, celery, docker, gnn, cybersecurity
```

### 3.4 Enable Actions

Go to: Settings → Actions → General

- **Actions permissions**: Allow all actions and reusable workflows
- **Workflow permissions**: Read and write permissions

### 3.5 Enable Discussions

Go to: Settings → Features → Enable Discussions

### 3.6 Enable Issues

Go to: Settings → Features → Enable Issues

### 3.7 Enable Wiki

Go to: Settings → Features → Enable Wiki

### 3.8 Enable Pages

Go to: Settings → Pages → Enable GitHub Pages
- Source: `/(root)`
- Branch: `main`
- Folder: `/(root)`

---

## Step 4: Create GitHub Project Board

1. Go to: Projects → New project
2. Choose **Board** template
3. Name: `GNAT Development`
4. Create columns:
   - `Backlog`
   - `Ready`
   - `In Progress`
   - `Code Review`
   - `Testing`
   - `Done`

---

## Step 5: Create Initial Issues

Create these issues to track Phase 2 and beyond:

### Issue #1: Phase 2 - Synthetic Data Generator
```
Type: Feature
Title: [FEATURE] Implement Synthetic Data Generator
Labels: feature, backend, database
Priority: High
```

### Issue #2: Phase 2 - Data Models
```
Type: Feature
Title: [FEATURE] Implement Data Models (Country, City, Dataset)
Labels: feature, database, backend
Priority: High
```

### Issue #3: Phase 3 - Graph Construction Engine
```
Type: Feature
Title: [FEATURE] Implement Graph Construction Engine
Labels: feature, ai, backend
Priority: High
```

---

## Step 6: Update README with Repository Links

Edit `README.md` and replace placeholder URLs:

```markdown
- Repository: https://github.com/YOUR_USERNAME/GNAT
- Issues: https://github.com/YOUR_USERNAME/GNAT/issues
- Documentation: https://YOUR_USERNAME.github.io/GNAT
```

---

## Step 7: Enable Repository Security Features

### 7.1 Dependabot Alerts

Go to: Settings → Security → Analysis → ✅ Dependabot alerts

### 7.2 Dependabot Security Updates

Go to: Settings → Security → Analysis → ✅ Dependabot security updates

### 7.3 Code Scanning

Go to: Settings → Security → Analysis → ✅ Code scanning

### 7.4 Secret Scanning

Go to: Settings → Security → Analysis → ✅ Secret scanning

---

## Step 8: Create .github/dependabot.yml

```yaml
version: 2
updates:
  # Update Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "YOUR_USERNAME"

  # Update GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
    open-pull-requests-limit: 5
```

Commit and push:
```bash
git add .github/dependabot.yml
git commit -m "ci(dependabot): add Dependabot configuration"
git push origin develop
```

---

## Step 9: Configure GitHub Actions Secrets

Go to: Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Name | Value | Description |
|------|-------|-------------|
| `DOCKER_REGISTRY` | `docker.io` | Docker registry |
| `DOCKER_USERNAME` | `your-docker-username` | Docker Hub username |
| `DOCKER_PASSWORD` | `your-docker-token` | Docker Hub access token |

---

## Step 10: Branch Strategy

Now that your repository is set up, follow this workflow:

### Development Workflow

```bash
# Always start from develop
git checkout develop
git pull origin develop

# Create a feature branch
git checkout -b feature/<module-name>

# Work on your feature
# Make commits following Conventional Commits
git add .
git commit -m "feat(module): add new feature"

# Push your branch
git push -u origin feature/<module-name>

# Create Pull Request on GitHub
# Link to issue: Closes #XX

# After review and merge
git checkout develop
git pull origin develop
git branch -d feature/<module-name>
git push origin --delete feature/<module-name>
```

### Release Workflow

```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/vX.Y.Z

# Finalize release (version bump, changelog, etc.)
# Tag the release
git tag -a vX.Y.Z -m "Release version X.Y.Z"

# Push to main
git checkout main
git merge release/vX.Y.Z
git push origin main
git push origin vX.Y.Z

# Merge back to develop
git checkout develop
git merge release/vX.Y.Z
git push origin develop

# Delete release branch
git branch -d release/vX.Y.Z
git push origin --delete release/vX.Y.Z
```

---

## Step 11: Verify Setup

Run these commands to verify everything is working:

```bash
# Check remotes
git remote -v

# Check branches
git branch -a

# Check status
git status

# Try fetching
git fetch origin
```

---

## Step 12: Quick Reference

### Common Commands

```bash
# Pull latest changes
git pull origin develop

# Sync fork with upstream (if using fork)
git fetch upstream
git checkout develop
git merge upstream/develop
git push origin develop

# View commit history
git log --oneline --graph --all

# View branch graph
git log --all --decorate --oneline --graph

# Clean up branches
git branch -d <branch-name>
git push origin --delete <branch-name>

# Stash changes
git stash push -m "Work in progress"

# Apply stashed changes
git stash pop
```

### Pull Request Checklist

Before creating a PR, ensure:
- [ ] Branch is up to date with develop
- [ ] All tests pass locally
- [ ] Code is formatted (black, isort)
- [ ] Linting passes (flake8)
- [ ] Type checking passes (mypy)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Related issue is linked

---

## Troubleshooting

### Authentication Error

If you get `Authentication failed`:

1. Check your PAT has correct scopes
2. Try using GitHub CLI: `gh auth login`
3. Update remote URL:
   ```bash
   git remote set-url origin https://YOUR_USERNAME@github.com/YOUR_USERNAME/GNAT.git
   ```

### Push Rejected

If you get `remote rejected`:

```bash
# Pull with rebase
git pull origin develop --rebase

# Resolve conflicts if any
# Then push
git push origin develop
```

### Branch Out of Sync

To sync a branch:

```bash
# Check out target branch
git checkout develop
git pull origin develop

# Check out your branch
git checkout feature/your-branch
git rebase develop
```

---

## Next Steps

Your GitHub repository is now professionally set up! Here's what to do next:

1. ✅ **Phase 1 Complete**: Project initialization done
2. 📝 **Create Issue**: Create an issue for Phase 2
3. 🔀 **Create Branch**: `git checkout -b feature/synthetic-data-generator`
4. 💻 **Implement**: Follow the specification in `07_SYNTHETIC_DATA_ENGINE.md`
5. ✅ **Test**: Run tests and ensure quality gates pass
6. 📝 **PR**: Create pull request with detailed description
7. 🔍 **Review**: Address review feedback
8. ✅ **Merge**: Merge to develop
9. 🔗 **Close**: Close the associated issue

---

## Support

If you encounter any issues:

- GitHub Docs: https://docs.github.com/
- Git Docs: https://git-scm.com/doc
- Open an issue: https://github.com/YOUR_USERNAME/GNAT/issues

---

**Repository Setup Complete! 🎉**