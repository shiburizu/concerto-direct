# concerto-direct
Visual front end for CCCaster 3.0022.

## Usage
To use it, just drop concerto.exe in the same folder as CCCaster. You need to be using the latest version of CCCaster and your caster EXE needs to be named "cccaster.v3.0.exe" to work.

Other players can connect to your online versus host without Concerto as long as they use the same version of CCCaster.

This program is only tested on Windows 10 for the time being. For best usage don't open CCCaster or MBAA.exe on their own while using this program.

## Build information

Dependencies:
* pywinpty
* Kivy[base]

To build, point pyinstaller at concerto.spec. keep all files in this zip in the same directory at build time.

Build command used: pyinstaller concerto.spec -F -i concertoicon.ico --upx-dir upx -w   

## Caveats

* Expect bugs
* REALLY long names totally break this I suspect
* Cannot change your name in the UI
* Cannot set port in UI
* Several advanced features are not available yet from the UI
