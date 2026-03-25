# Topic: GitHub Actions — CI/CD Pipeline

**Time:** 15 min
**Goal:** Auto-test and deploy on push to main

---

## What to Search
- "GitHub Actions deploy Azure App Service Python"
- "GitHub Actions pytest workflow"

## Workflow File (.github/workflows/deploy.yml)
```yaml
name: Test & Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: orgmind_test
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
        env:
          POSTGRES_URL: postgresql://postgres:test@localhost:5432/orgmind_test

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - run: |
          zip -r deploy.zip . -x ".git/*" "__pycache__/*" "tests/*" ".env"
          az webapp deploy --name orgmind-bot --resource-group orgmind-rg --src-path deploy.zip --type zip
```

## What to Understand
- [ ] Tests run on every PR and push to main
- [ ] PostgreSQL spins up as service container
- [ ] Deploy only runs on main branch (not PRs)
- [ ] `AZURE_CREDENTIALS` secret must be set in GitHub repo settings
- [ ] Tests use test database, not production
