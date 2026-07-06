# Releasing

Maintainer notes. Users don't need anything here — see [README.md](README.md).

## What a tag push does

Pushing a `v*` tag runs `.github/workflows/release.yml`:

1. **Guard** — the tag must equal `project.version` in `pyproject.toml`,
   or every job fails immediately.
2. **Build wheels** (one per platform, each bundling only its matching
   server binary, downloaded and SHA-256-verified at build time):
   - `win_amd64` — `gomc-rest.exe`
   - `manylinux_2_34_x86_64` — `gomc-rest-linux-amd64` (dynamically linked,
     needs glibc ≥ 2.34; hence the 2_34 tag)
   - `manylinux2014_aarch64` — `gomc-rest-linux-arm64` (statically linked)
3. **Build sdist** — no binary; the client-only fallback for platforms
   without a wheel (macOS, Windows arm64, older glibc).
4. **Publish to PyPI** — trusted publishing (OIDC) via the `pypi`
   environment. `skip-existing` makes re-running a tag safe.
5. **GitHub Release** — created only after PyPI publish succeeds, with
   generated notes and all dist files attached as assets.

`workflow_dispatch` runs the builds for verification but never publishes.

## Cutting a release

1. Bump the package version in **both** places (they must match the tag):
   - `pyproject.toml` → `project.version`
   - `src/gomc_rest/__init__.py` → `__version__`
2. Merge to `main`, then tag that exact version:

   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

If publish fails transiently, fix and re-push the same tag — PyPI skips
files it already has, and the release job then attaches the assets.

## Bumping the bundled gomc-rest server

Only needed when changing the bundled server version:

1. Edit `GOMC_REST_VERSION`. Keep it within the range accepted by the
   pinned `gomc-rest-client` (its `MINIMUM_SUPPORTED_GOMC_REST_VERSION`);
   bump the client pin in `pyproject.toml` together if needed.
2. Add `checksums/<version>.sha256` with the trusted SHA-256 of each
   release asset (`gomc-rest.exe`, `gomc-rest-linux-amd64`,
   `gomc-rest-linux-arm64`). These are committed so a swapped release
   asset is detected; vendoring fails closed without them.
3. If the new binaries change their glibc requirement (check with
   `readelf -V <binary> | grep GLIBC`), update the `plat` tags in
   `release.yml` and the CI floor test image in `ci.yml`.

## Local builds (testing without PyPI)

```bash
python scripts/vendor_binaries.py            # fetch + verify all binaries
python -m build --wheel
python -m wheel tags --platform-tag manylinux_2_34_x86_64 --remove dist/*.whl
python -m build --sdist                      # remove binaries first for a clean sdist
```

## One-time infrastructure (already done)

- PyPI trusted publisher: repo `Moge800/gomc_rest_python`, workflow
  `release.yml`, environment `pypi`.
- GitHub environment `pypi` on the repository.
