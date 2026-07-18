# Releasing

Maintainer notes. Users don't need anything here — see [README.md](README.md).

## What a tag push does

Pushing a `v*` tag runs `.github/workflows/release.yml`:

1. **Version** — derived from the tag itself by hatch-vcs
   (`dynamic = ["version"]`); there is no version string to keep in sync.
2. **Build wheels** (one per platform, each bundling only its matching
   server binary, downloaded and SHA-256-verified at build time):
   - `win_amd64` — `gomc-rest.exe`
   - `manylinux_2_34_x86_64` — `gomc-rest-linux-amd64` (dynamically linked,
     needs glibc ≥ 2.34; hence the 2_34 tag)
   - `manylinux2014_aarch64` — `gomc-rest-linux-arm64` (statically linked)
   - `macosx_12_0_x86_64` (`macos-13` runner) — `gomc-rest-darwin-amd64`,
     unsigned
   - `macosx_12_0_arm64` (`macos-14` runner) — `gomc-rest-darwin-arm64`,
     ad-hoc signed (Apple Silicon requires at least ad-hoc signing to run
     at all)

   Both darwin binaries declare a minimum OS of macOS 12 via
   `LC_BUILD_VERSION`, hence the `macosx_12_0` tags. `ci.yml`'s
   `test-macos` job actually launches the server on both real macOS
   runners on every PR — the authoritative check for Gatekeeper/signing
   behavior, since inspecting the binary can't fully predict it.
3. **Build sdist** — no binary; the client-only fallback for platforms
   without a wheel (Windows arm64, older glibc, macOS < 12).
4. **Publish to PyPI** — trusted publishing (OIDC) via the `pypi`
   environment. `skip-existing` makes re-running a tag safe.
5. **GitHub Release** — created only after PyPI publish succeeds, with
   generated notes and all dist files attached as assets.

`workflow_dispatch` runs the builds for verification but never publishes.

## Cutting a release

Tag `main` and push — that's all. The version comes from the tag
(hatch-vcs), and `__version__` reads the installed package metadata, so
there is nothing to bump anywhere.

```bash
git tag v0.2.0
git push origin v0.2.0
```

Untagged builds get a dev version like `0.1.3.dev2+g1234abc` — handy for
telling local builds apart from releases.

If publish fails transiently, re-run the failed jobs for that tag's run
from the GitHub Actions UI — PyPI skips files it already has, and the
release job then attaches the assets. Only delete and recreate the tag if
the fix requires new commits (which means a new version anyway).

## Bumping the bundled gomc-rest server

Only needed when changing the bundled server version:

1. Edit `GOMC_REST_VERSION`. Keep it within the range accepted by the
   pinned `gomc-rest-client` (its `MINIMUM_SUPPORTED_GOMC_REST_VERSION`);
   bump the client pin in `pyproject.toml` together if needed.
2. Add `checksums/<version>.sha256` with the trusted SHA-256 of each
   release asset (`gomc-rest.exe`, `gomc-rest-linux-amd64`,
   `gomc-rest-linux-arm64`, `gomc-rest-darwin-amd64`,
   `gomc-rest-darwin-arm64`). These are committed so a swapped release
   asset is detected; vendoring fails closed without them.
3. If the Linux binaries change their glibc requirement (check with
   `readelf -V <binary> | grep GLIBC`), update the `plat` tags in
   `release.yml` and the CI floor test image in `ci.yml`. If the darwin
   binaries change their minimum OS (check with `otool -l <binary> | grep
   -A3 LC_BUILD_VERSION`, or parse the load command directly), update the
   `macosx_*` tags in `release.yml`.

## Local builds (testing without PyPI)

```bash
python scripts/vendor_binaries.py            # fetch + verify all binaries
python -m build --wheel
python -m wheel tags --platform-tag manylinux_2_34_x86_64 --remove dist/*.whl
rm src/gomc_rest/binaries/gomc-rest*         # drop vendored binaries for a clean sdist
python -m build --sdist
```

## One-time infrastructure (already done)

- PyPI trusted publisher: repo `Moge800/gomc_rest_python`, workflow
  `release.yml`, environment `pypi`.
- GitHub environment `pypi` on the repository.
