# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['backend\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('backend/templates', 'backend/templates'), ('backend/credentials', 'backend/credentials')],
    hiddenimports=['google.oauth2.credentials', 'google.auth.transport.requests'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MyztrixAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
