# GitHub Actions CI/CD (Code-Ready Reference)

> For Claude Code: Automated testing and deployment pipeline.

## `.github/workflows/ci.yml`

```yaml
name: CI
on: [push, pull_request]

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
      - run: pip install -e ".[dev]"
      - run: pytest --cov=orgmind --cov-report=xml
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SUPERMEMORY_API_KEY: ${{ secrets.SUPERMEMORY_API_KEY }}
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
          zip -r deploy.zip . -x ".git/*" "__pycache__/*" ".env" "tests/*"
          az webapp deploy --name orgmind-bot --resource-group orgmind-rg --src-path deploy.zip --type zip
```

## IMPORTANT NOTES
1. Run tests with real Postgres (via services)
2. Mock LLM calls in tests — don't burn API credits in CI
3. Deploy only from `main` branch after tests pass
4. Store API keys in GitHub Secrets
