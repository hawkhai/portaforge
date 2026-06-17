#encoding=utf8
import os
import subprocess

from gen_manifest import update_manifest


DEFAULT_NSIS = r"C:\Program Files (x86)\NSIS\NSIS.exe"
DEFAULT_WEBSITE = "https://wordtap.cn"


def _nsis_quote(text):
    return str(text).replace("$", "$$").replace('"', '$\\"')


def _find_makensis(nsis_path=DEFAULT_NSIS):
    candidates = []
    if nsis_path:
        nsis_path = os.path.abspath(nsis_path)
        nsis_dir = os.path.dirname(nsis_path)
        candidates.extend([
            os.path.join(nsis_dir, "makensis.exe"),
            nsis_path,
        ])
    candidates.extend([
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "makensis.exe",
    ])

    for candidate in candidates:
        if candidate.endswith(".exe") and os.path.exists(candidate):
            if os.path.basename(candidate).lower() == "makensis.exe":
                return candidate
    return "makensis.exe"


def _find_entry_exe(app_dir, entry=""):
    if entry:
        entry_name = entry if entry.lower().endswith(".exe") else entry + ".exe"
        entry_path = os.path.join(app_dir, entry_name)
        if not os.path.exists(entry_path):
            raise AssertionError("entry exe not found: {}".format(entry_path))
        return entry_name

    exes = [name for name in os.listdir(app_dir) if name.lower().endswith(".exe")]
    if len(exes) != 1:
        raise AssertionError(
            "entry exe is ambiguous, specify via --entry (found: {})".format(exes)
        )
    return exes[0]


def _app_version(app_dir, fallback="1.0.0"):
    entry_names = [name for name in os.listdir(app_dir) if name.lower().endswith(".exe")]
    if entry_names:
        stamp = int(os.path.getmtime(os.path.join(app_dir, entry_names[0])))
        return "1.0.{}".format(stamp)
    return fallback


def _dir_size_kb(path):
    total = 0
    for root, dirs, names in os.walk(path):
        for name in names:
            total += os.path.getsize(os.path.join(root, name))
    return max(1, total // 1024)


def _vi_product_version(version):
    parts = []
    for part in str(version).split("."):
        try:
            parts.append(str(max(0, min(65535, int(part)))))
        except ValueError:
            parts.append("0")
    while len(parts) < 4:
        parts.append("0")
    return ".".join(parts[:4])


def gen_nsis_script(app, icon, entry="", outdir="dist", nsis=DEFAULT_NSIS,
                    app_name="", publisher="", version="", msi=False,
                    language="SimpChinese", website=DEFAULT_WEBSITE):
    if msi:
        raise AssertionError(
            "NSIS cannot build a real MSI directly. Use the NSIS .exe installer, "
            "or install WiX and add a separate MSI backend."
        )

    app_dir = os.path.abspath(app)
    if not os.path.isdir(app_dir):
        raise AssertionError("app directory not found: {}".format(app_dir))

    entry_exe = _find_entry_exe(app_dir, entry=entry)
    app_name = app_name or os.path.basename(os.path.normpath(app))
    publisher = publisher or app_name
    version = version or _app_version(app_dir)
    vi_version = _vi_product_version(version)
    estimated_size = _dir_size_kb(app_dir)
    outdir = os.path.abspath(outdir)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    script_dir = os.path.join("build", "nsis")
    if not os.path.isdir(script_dir):
        os.makedirs(script_dir)

    script_path = os.path.abspath(os.path.join(script_dir, "{}.nsi".format(app_name)))
    outfile = os.path.abspath(os.path.join(outdir, "{}-Setup.exe".format(app_name)))
    icon_abs = os.path.abspath(icon) if icon else ""
    if icon_abs and not os.path.exists(icon_abs):
        raise AssertionError("icon not found: {}".format(icon_abs))

    uninstall_key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{}".format(app_name)
    app_reg_key = r"Software\{}".format(app_name)

    icon_lines = ""
    if icon_abs:
        icon_lines = '''
!define MUI_ICON "{}"
!define MUI_UNICON "{}"'''.format(_nsis_quote(icon_abs), _nsis_quote(icon_abs))

    old_uninstall_shortcut = "卸载.lnk"
    uninstall_shortcut = "卸载 {}.lnk".format(app_name)

    script = r'''
Unicode True
ManifestDPIAware True
SetCompressor /SOLID lzma
SetCompressorDictSize 64
RequestExecutionLevel user

!include MUI2.nsh

!define APP_NAME "{app_name}"
!define APP_VERSION "{version}"
!define APP_PUBLISHER "{publisher}"
!define APP_EXE "{entry_exe}"
!define APP_WEBSITE "{website}"
{icon_lines}

VIProductVersion "{vi_version}"
VIAddVersionKey "ProductName" "${{APP_NAME}}"
VIAddVersionKey "ProductVersion" "${{APP_VERSION}}"
VIAddVersionKey "CompanyName" "${{APP_PUBLISHER}}"
VIAddVersionKey "FileDescription" "${{APP_NAME}} Installer"
VIAddVersionKey "FileVersion" "${{APP_VERSION}}"
VIAddVersionKey "InternalName" "${{APP_NAME}} Setup"
VIAddVersionKey "OriginalFilename" "${{APP_NAME}}-Setup.exe"
VIAddVersionKey "Comments" "${{APP_WEBSITE}}"
VIAddVersionKey "LegalCopyright" "${{APP_WEBSITE}}"

Name "${{APP_NAME}}"
OutFile "{outfile}"
InstallDir "$LOCALAPPDATA\Programs\${{APP_NAME}}"
InstallDirRegKey HKCU "{app_reg_key}" "InstallDir"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${{APP_EXE}}"
!define MUI_FINISHPAGE_RUN_TEXT "运行 ${{APP_NAME}}"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "{language}"

Section "安装"
  SetShellVarContext current
  SetOutPath "$INSTDIR"
  File /r "{app_dir}\*.*"

  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "{app_reg_key}" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "{uninstall_key}" "DisplayName" "${{APP_NAME}}"
  WriteRegStr HKCU "{uninstall_key}" "DisplayVersion" "${{APP_VERSION}}"
  WriteRegStr HKCU "{uninstall_key}" "Publisher" "${{APP_PUBLISHER}}"
  WriteRegStr HKCU "{uninstall_key}" "URLInfoAbout" "${{APP_WEBSITE}}"
  WriteRegStr HKCU "{uninstall_key}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "{uninstall_key}" "DisplayIcon" "$INSTDIR\${{APP_EXE}}"
  WriteRegStr HKCU "{uninstall_key}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegStr HKCU "{uninstall_key}" "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
  WriteRegDWORD HKCU "{uninstall_key}" "EstimatedSize" {estimated_size}
  WriteRegDWORD HKCU "{uninstall_key}" "NoModify" 1
  WriteRegDWORD HKCU "{uninstall_key}" "NoRepair" 1

  CreateDirectory "$SMPROGRAMS\${{APP_NAME}}"
  CreateDirectory "$DESKTOP"
  Delete "$SMPROGRAMS\${{APP_NAME}}\{old_uninstall_shortcut}"
  CreateShortcut "$SMPROGRAMS\${{APP_NAME}}\${{APP_NAME}}.lnk" "$INSTDIR\${{APP_EXE}}"
  CreateShortcut "$SMPROGRAMS\${{APP_NAME}}\{uninstall_shortcut}" "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\${{APP_NAME}}.lnk" "$INSTDIR\${{APP_EXE}}"
SectionEnd

Section "Uninstall"
  SetShellVarContext current
  Delete "$DESKTOP\${{APP_NAME}}.lnk"
  RMDir /r "$SMPROGRAMS\${{APP_NAME}}"
  DeleteRegKey HKCU "{uninstall_key}"
  DeleteRegKey HKCU "{app_reg_key}"
  RMDir /r "$INSTDIR"
SectionEnd
'''.format(
        app_name=_nsis_quote(app_name),
        version=_nsis_quote(version),
        publisher=_nsis_quote(publisher),
        entry_exe=_nsis_quote(entry_exe),
        website=_nsis_quote(website),
        vi_version=vi_version,
        icon_lines=icon_lines,
        language=_nsis_quote(language),
        old_uninstall_shortcut=_nsis_quote(old_uninstall_shortcut),
        uninstall_shortcut=_nsis_quote(uninstall_shortcut),
        estimated_size=estimated_size,
        outfile=_nsis_quote(outfile),
        app_dir=_nsis_quote(app_dir),
        app_reg_key=_nsis_quote(app_reg_key),
        uninstall_key=_nsis_quote(uninstall_key),
    ).strip() + "\r\n"

    with open(script_path, "wb") as fp:
        fp.write(script.encode("utf-8-sig"))

    return script_path, outfile, _find_makensis(nsis)


def build_nsis(app, icon, entry="", outdir="dist", nsis=DEFAULT_NSIS,
               app_name="", publisher="", version="", msi=False,
               language="SimpChinese", website=DEFAULT_WEBSITE):
    update_manifest(app, entry=entry)
    script_path, outfile, makensis = gen_nsis_script(
        app, icon, entry=entry, outdir=outdir, nsis=nsis,
        app_name=app_name, publisher=publisher, version=version,
        msi=msi, language=language, website=website)
    cmd = [makensis, "/V2", script_path]
    print(" ".join(cmd))
    subprocess.check_call(cmd)
    return outfile
