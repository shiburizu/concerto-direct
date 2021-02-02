# concerto-direct
Visual front end for CCCaster 3.0022.

## Usage
To use it, just drop concerto.exe in the same folder as CCCaster. You need to be using the latest version of CCCaster and your caster EXE needs to be named "cccaster.v3.0.exe" to work.

Other players can connect to your online versus host without Concerto as long as they use the same version of CCCaster.

This program is only tested on Windows 10 for the time being. For best usage don't open CCCaster or MBAA.exe on their own while using this program.

## Build information

**Concerto currently only works with Python 3.6. This is because of pywinpty.**

* Latest prebuilt version here: https://www.python.org/downloads/release/python-368/

Dependencies:
* pywinpty
* Kivy

To build, point pyinstaller at concerto.spec. keep all files in this zip in the same directory at build time. winpty-agent.exe needs to be included in the onefile.

* winpty-agent.exe which comes from Spyder-IDE and is licensed under MIT. 
* Python 3.9 support is being investigated for pywinpty, see here: https://github.com/jupyter/notebook/issues/5967

## Caveats

* Reading the caster output is not always perfect so names may be incorrectly displayed
* REALLY long names totally break this I suspect
* Cannot change your name in the UI
* Several advanced features are not available yet from the UI
