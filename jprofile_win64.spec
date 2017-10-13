# -*- mode: python -*-
a = Analysis(['.\cli.py'],
             pathex=['.\jprofile'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win64\\jprofile', 'jprofile.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True )

profiles_tree = Tree('./jprofile/profiles', prefix = 'profiles')
schemas_tree = Tree('./jprofile/schemas', prefix = 'schemas')
# Following is an ugly hack, because these lxml files aren't packaged correctly by default
resources_tree = Tree('./jprofile/jprofile.exe%3F175104', prefix = 'jprofile.exe%3F175104')
          
coll = COLLECT(exe,
               a.binaries +
               [('./license/LICENSE.txt','LICENSE','DATA')],
               resources_tree,
               profiles_tree,
               schemas_tree,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist_win64', 'jprofile'))
