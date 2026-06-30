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

For Home Assistant add-on releases, wait for the tagged publish workflow to finish before announcing the version as ready. Then verify the GHCR tag exists:

```bash
python3 scripts/verify_release_image.py --version <version>
```

Keep private databases, private seed catalogs, exports, and backups out of git. Public examples must stay generic.
