# GitHub Setup Checklist

## ✅ Pre-Push Checklist

- [ ] **Local environment verified**: Run `just check-ci` and ensure all checks pass
- [ ] **Code quality verified**: Run `just lint`, `just typecheck`, `just test-quick`  
- [ ] **Badge URLs updated**: Replace `axgkl` with your GitHub username in README.md
- [ ] **Dependencies synced**: Run `uv sync --dev` to ensure lock file is current
- [ ] **License updated**: Replace "MYCOMPANY" with actual company name in LICENSE file

## ✅ Post-Push Checklist

### 1. Repository Secrets
- [ ] Go to **Settings → Secrets and variables → Actions**
- [ ] Add `PYPI_API_TOKEN` (get from [PyPI Account Settings](https://pypi.org/manage/account/))
- [ ] Add `CODECOV_TOKEN` (optional, get from [Codecov.io](https://codecov.io/))

### 2. Release Environment
- [ ] Go to **Settings → Environments**
- [ ] Create `release` environment  
- [ ] Add protection rules (require reviewers for releases)
- [ ] Add `PYPI_API_TOKEN` to release environment secrets

### 3. Branch Protection
- [ ] Go to **Settings → Branches**
- [ ] Add rule for `main` branch
- [ ] Enable **"Require status checks before merging"**
- [ ] Select required checks:
  - [ ] `Test Python 3.8 on ubuntu-latest`
  - [ ] `Test Python 3.11 on ubuntu-latest`
  - [ ] `Code Quality Checks`
- [ ] Enable **"Require up-to-date branches"**

### 4. Verify Workflows
- [ ] Check **Actions** tab - workflows should be running
- [ ] Verify badges update in README (may take a few minutes)
- [ ] Check **Dependabot** tab for dependency update PRs

### 5. Test Release Process
- [ ] Create test tag: `git tag v3.0.3-test`
- [ ] Push tag: `git push origin v3.0.3-test`
- [ ] Verify release workflow runs successfully
- [ ] Delete test tag: `git tag -d v3.0.3-test && git push origin :refs/tags/v3.0.3-test`

## 🔗 Quick Links (Update with your username)

- **Actions**: https://github.com/axgkl/ax_utils/actions
- **Settings**: https://github.com/axgkl/ax_utils/settings
- **Releases**: https://github.com/axgkl/ax_utils/releases
- **PyPI Package**: https://pypi.org/project/ax_utils/

## 🆘 If Something Goes Wrong

### Workflow Failures
1. Check **Actions** tab for detailed error logs
2. Compare with local `just check-ci` results
3. Verify all secrets are properly configured
4. Check branch protection rules aren't blocking required checks

### Badge Issues
1. Ensure workflow names match badge URLs exactly
2. Wait a few minutes for GitHub to update badge cache
3. Verify repository visibility (badges won't work for private repos without tokens)

### Release Issues
1. Confirm PyPI token has correct permissions
2. Check version number format (must start with 'v')
3. Verify all tests pass before creating release tag
4. Review release environment protection rules

## 📞 Support Resources

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **UV Documentation**: https://docs.astral.sh/uv/
- **PyPI Help**: https://pypi.org/help/
- **Ruff Documentation**: https://docs.astral.sh/ruff/

---

**Ready to push?** ✨ Your CI/CD pipeline is fully configured and ready to go!
