# Contributing

Family Menu is a local-first meal planning app packaged for local development and Home Assistant.

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
cd family-menu/frontend
npm install
npm run build
cd ../..
.venv/bin/python -m pytest -q
```

Keep private databases, private seed catalogs, exports, and backups out of git. Public examples must stay generic.
