To release new version:

- Update version in pyproject.toml and npm-package/package.json
- Build npm package from npm-package/ with `npm run build`
  - (This will run `build_pyz.py` and `build_npm_package.py`)
- Test if it works with npm-link. A version, once published, can never be published again, even if it was unpublished.
  - Run create-link from npm-package/
  - Run py-link from vs-prince
- Publish beta release: `npm publish --tag beta`
- Promote to latest version:
  - `npm dist-tag add @mhidvegi/pyprince@<version> latest`
- Optionally remove beta tag
  - `npm dist-tag rm @mhidvegi/pyprince@<version> beta`
