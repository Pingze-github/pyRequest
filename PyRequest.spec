# -*- mode: python -*-

block_cipher = None


a = Analysis(['index.py'],
             pathex=['F:\\git\\pyRequest'],
             binaries=[],
             datas=[('assets/icon.ico', 'assets'), ('assets/MSYHMONO.ttf', 'assets')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='PyRequest',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='assets\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='PyRequest')
