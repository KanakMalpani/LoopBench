# Publishing LoopBench to PyPI

**Prerequisite:** [LoopGym](https://pypi.org/project/loopgym/) must be published first — LoopBench depends on `loopgym>=0.1.0`.

## One-time setup

1. Create a PyPI project named **`loopbench`**.
2. Add **`PYPI_API_TOKEN`** to this repo's Actions secrets.

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
