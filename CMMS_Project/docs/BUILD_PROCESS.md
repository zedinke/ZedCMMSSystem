# Build Process Documentation

## Overview

This document describes the process for building a Windows executable from the CMMS source code using PyInstaller.

## Prerequisites

1. **Python 3.10+** installed
2. **Virtual environment** activated (`.venv`)
3. **All dependencies** installed:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

## Build Steps

### 1. Prepare the Environment

```bash
cd CMMS_Project
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

### 2. Verify Dependencies

Ensure all required packages are installed:
```bash
pip list | grep -E "flet|sqlalchemy|pandas|openpyxl|matplotlib|qrcode|docx|bcrypt|alembic"
```

### 3. Run Build Script

```bash
python build.py
```

Or manually:
```bash
python -m PyInstaller --clean --noconfirm build.spec
```

## Build Configuration

### build.spec File

The `build.spec` file contains the PyInstaller configuration:

- **Entry Point**: `main.py`
- **Data Files**: 
  - Localization JSON files
  - DOCX templates
  - Configuration files
  - Images (logo)
  - Alembic migration files
- **Hidden Imports**: All required Python modules
- **Output**: `dist/CMMS.exe`

### Included Files

The build includes:
- All Python source files
- Translation files (`localization/translations/*.json`)
- Templates (`templates/*.docx`, `templates/*.json`)
- Configuration files (`config/*.py`)
- Images (`Images/*.jpg`, `Images/*.png`)
- Database migrations (`migrations/versions/*.py`)
- Alembic configuration (`alembic.ini`)

## Output

After successful build:
- **Executable**: `dist/CMMS.exe`
- **Build artifacts**: `build/` directory (can be deleted)
- **Distribution**: `dist/` directory

## Testing the Executable

1. Navigate to `dist/` directory
2. Run `CMMS.exe`
3. Test all major features:
   - Login
   - Asset management
   - Inventory management
   - Worksheet creation
   - Report generation
   - Settings

## Troubleshooting

### Import Errors

If the executable fails with import errors:
1. Check `hiddenimports` in `build.spec`
2. Add missing modules to `hiddenimports`
3. Rebuild

### Missing Data Files

If data files are missing:
1. Check `datas` section in `build.spec`
2. Verify file paths are correct
3. Ensure files exist in source directory
4. Rebuild

### Large Executable Size

The executable may be large (100-200 MB) due to:
- Python runtime
- All dependencies bundled
- Data files included

To reduce size:
- Use `--onefile` mode (already enabled)
- Exclude unused modules
- Use UPX compression (enabled in spec)

### Database Migration Issues

If database migrations fail:
1. Ensure `migrations/` directory is included in `datas`
2. Check `alembic.ini` is included
3. Verify migration files are present

## Distribution

### Creating Installer (Optional)

For distribution, consider creating an installer using:
- **NSIS** (Nullsoft Scriptable Install System)
- **Inno Setup**
- **WiX Toolset**

### Requirements for Distribution

1. **Executable**: `dist/CMMS.exe`
2. **Documentation**: Include `docs/` folder
3. **README**: Include `README.md`
4. **License**: Include license file (if applicable)

## Version Information

The executable version is read from `version.txt` at runtime.

To update version:
1. Edit `version.txt`
2. Rebuild executable

## Build Optimization

### UPX Compression

UPX compression is enabled in `build.spec` to reduce executable size.

### One-file Mode

The build uses one-file mode, creating a single executable file.

### Console Window

Console window is disabled (`console=False`) for a cleaner user experience.

## Maintenance

### Updating Dependencies

When adding new dependencies:
1. Update `requirements.txt`
2. Add to `hiddenimports` in `build.spec` if needed
3. Rebuild

### Adding New Data Files

When adding new data files:
1. Add to `datas` section in `build.spec`
2. Rebuild

## Notes

- The build process takes 2-5 minutes depending on system
- First build may take longer
- Subsequent builds are faster due to caching
- Always test the executable before distribution

---

**Last Updated**: 2025-12-14  
**Build Tool**: PyInstaller  
**Python Version**: 3.10+

