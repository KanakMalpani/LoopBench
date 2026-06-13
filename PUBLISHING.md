# Publishing LoopBench to PyPI

**Prerequisite:** [LoopGym](https://pypi.org/project/loopgym/) must be published first.

## One-time setup

1. Create a PyPI project named **`loopbench`**.
2. Configure [trusted publishing](https://docs.pypi.org/trusted-publishers/) (OIDC):
   - **Owner:** `KanakMalpani`
   - **Repository:** `LoopBench`
   - **Workflow:** `publish.yml`
   - **Environment:** *(leave blank)*

3. *(Optional fallback)* Add **`PYPI_API_TOKEN`** to this repo's Actions secrets.

## Publish

```bash
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 --title "v0.1.0" --notes "Initial public release"
```

Or trigger **Actions → Publish to PyPI** manually.

## Install

```bash
pip install loopbench loopgym
loopbench list
```

## Verify locally

```bash
pip install -e ../LoopGym
pip install build
python -m build
pip install dist/loopbench-*.whl
pytest tests/ -q
```
