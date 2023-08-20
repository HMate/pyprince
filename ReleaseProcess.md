To release new version:

- Update version in pyproject.toml and npm-package/package.json
- Build npm package from npm-package/ with `npm run build`
- Test if it works with npm-link. A version, once published, can never be published again, even if it was unpublished.
- Publish beta release: `npm publish --tag beta`
- Promote to latest version:
  - `npm dist-tag add @mhidvegi/pyprince@<version> latest`
- Optionally remove beta tag
  - `npm dist-tag rm @mhidvegi/pyprince@<version> beta`
