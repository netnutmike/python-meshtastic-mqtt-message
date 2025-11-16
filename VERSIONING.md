# Versioning and Release Management

This document describes the versioning strategy and release process for Meshtastic MQTT CLI.

## Versioning Strategy

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality in a backwards compatible manner
- **PATCH** version: Backwards compatible bug fixes

Current version: **0.1.0**

## Version Files

Version information is stored in:
- `src/meshtastic_mqtt_cli/__version__.py` - Single source of truth
- `src/meshtastic_mqtt_cli/__init__.py` - Exports version for package
- `setup.py` - Reads version from `__version__.py`

## Checking Version

### From Command Line
```bash
meshtastic-send --version
```

### From Python
```python
from meshtastic_mqtt_cli import __version__, __version_info__

print(__version__)        # "0.1.0"
print(__version_info__)   # (0, 1, 0)
```

## Bumping Version

Use the provided script to bump version numbers:

```bash
# Bump patch version (0.1.0 -> 0.1.1)
python scripts/bump_version.py patch

# Bump minor version (0.1.0 -> 0.2.0)
python scripts/bump_version.py minor

# Bump major version (0.1.0 -> 1.0.0)
python scripts/bump_version.py major

# Dry run to see what would change
python scripts/bump_version.py patch --dry-run
```

The script will:
1. Update `src/meshtastic_mqtt_cli/__version__.py`
2. Update `CHANGELOG.md` with new version and date
3. Show next steps for committing and tagging

## Release Process

1. **Update CHANGELOG.md**
   - Document all changes under `[Unreleased]` section
   - Follow [Keep a Changelog](https://keepachangelog.com/) format

2. **Bump Version**
   ```bash
   python scripts/bump_version.py [major|minor|patch]
   ```

3. **Review Changes**
   ```bash
   git diff
   ```

4. **Run Tests**
   ```bash
   python -m unittest discover tests -v
   ```

5. **Commit Changes**
   ```bash
   git commit -am "chore: bump version to X.Y.Z"
   ```

6. **Create Git Tag**
   ```bash
   git tag vX.Y.Z
   ```

7. **Push to Repository**
   ```bash
   git push && git push --tags
   ```

8. **Create GitHub Release** (if using GitHub)
   - Go to repository releases
   - Create new release from tag
   - Copy changelog entries for this version
   - Publish release

## Dependency Management

### Renovate Bot

This project uses [Renovate](https://docs.renovatebot.com/) for automated dependency updates.

**Configuration:** `renovate.json`

**Features:**
- Automatically creates PRs for dependency updates
- Runs weekly on Mondays at 6:00 AM
- Auto-merges minor and patch updates
- Prioritizes security updates
- Limits concurrent PRs to avoid spam

**Renovate Settings:**
- Schedule: Before 6am on Monday
- Auto-merge: Minor and patch updates
- PR limit: 5 concurrent, 2 per hour
- Semantic commits: Enabled
- Vulnerability alerts: Enabled

### Manual Dependency Updates

To manually update dependencies:

```bash
# Update all dependencies to latest versions
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade paho-mqtt

# Regenerate requirements.txt
pip freeze > requirements.txt
```

### Checking for Outdated Dependencies

```bash
pip list --outdated
```

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## License

This project is licensed under GPL v3 - see [LICENSE](LICENSE) file.
