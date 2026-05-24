# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\src\\projects\\project_agent_manager\\src\\pam\\main.py'],
    pathex=['C:\\src\\projects\\project_agent_manager\\src'],
    binaries=[],
    datas=[('C:\\src\\projects\\project_agent_manager\\ai\\agents', 'ai/agents'), ('C:\\src\\projects\\project_agent_manager\\ai\\prompts', 'ai/prompts'), ('C:\\src\\projects\\project_agent_manager\\ai\\runtime_profiles', 'ai/runtime_profiles'), ('C:\\src\\projects\\project_agent_manager\\ai\\pipelines', 'ai/pipelines'), ('C:\\src\\projects\\project_agent_manager\\protocol', 'protocol'), ('C:\\src\\projects\\project_agent_manager\\.env.example', '.'), ('C:\\src\\projects\\project_agent_manager\\src\\pam\\templates', 'pam/templates')],
    hiddenimports=[],
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
    name='pam',
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
