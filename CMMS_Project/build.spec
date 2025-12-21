# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# Helper function to add datas only if files exist
def add_datas_if_exist(pattern, target_dir):
    """Add datas to the list only if files matching the pattern exist"""
    source_path = Path(pattern.split('/')[0])
    if not source_path.exists():
        return []
    files = list(source_path.glob(pattern.split('/')[-1]))
    if files:
        return [(pattern, target_dir)]
    return []

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('localization/translations/*.json', 'localization/translations'),
        ('templates/*.docx', 'templates'),
        ('templates/*.json', 'templates'),
        ('config/*.py', 'config'),
        ('migrations/versions/*.py', 'migrations/versions'),
        ('migrations/env.py', 'migrations'),
        ('migrations/script.py.mako', 'migrations'),
        ('alembic.ini', '.'),
        ('version.txt', '.'),
        ('installer/gdpr_agreement.txt', 'installer'),
        ('installer/terms_of_service.txt', 'installer'),
        ('Images/zedcmms_system.jpg', 'Images'),
    ] + add_datas_if_exist('Images/*.jpg', 'Images') + add_datas_if_exist('Images/*.png', 'Images'),
    hiddenimports=[
        'flet',
        'flet.core',
        'flet.core.control',
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.engine',
        'sqlalchemy.pool',
        'sqlalchemy.sql',
        'pandas',
        'openpyxl',
        'openpyxl.chart',
        'openpyxl.drawing',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'qrcode',
        'qrcode.image',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'docx',
        'docx.shared',
        'docx.enum.text',
        'bcrypt',
        'reportlab',
        'reportlab.graphics',
        'reportlab.graphics.barcode',
        'reportlab.graphics.barcode.code128',
        'reportlab.graphics.barcode.code39',
        'reportlab.graphics.barcode.code93',
        'reportlab.graphics.barcode.common',
        'reportlab.graphics.barcode.dmtx',
        'reportlab.graphics.barcode.eanbc',
        'reportlab.graphics.barcode.ecc200datamatrix',
        'reportlab.graphics.barcode.fourstate',
        'reportlab.graphics.barcode.lto',
        'reportlab.graphics.barcode.qr',
        'reportlab.graphics.barcode.qrencoder',
        'reportlab.graphics.barcode.usps',
        'reportlab.graphics.barcode.usps4s',
        'reportlab.graphics.barcode.widgets',
        'alembic',
        'alembic.runtime.migration',
        'alembic.script',
        'alembic.util',
        'threading',
        'asyncio',
        'concurrent.futures',
        'logging',
        'logging.handlers',
        'zipfile',
        'shutil',
        'pathlib',
        'datetime',
        'json',
        'csv',
        'io',
        'base64',
        'jaraco',
        'jaraco.functools',
        'jaraco.context',
        'jaraco.text',
        'pkg_resources._vendor.jaraco.functools',
        'pkg_resources._vendor.jaraco.context',
        'pkg_resources._vendor.jaraco.text',
        'schedule',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CMMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

