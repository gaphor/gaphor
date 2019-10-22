; Copyright 2016 Christoph Reiter, 2019 Dan Yeaw
;
; This program is free software; you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation; either version 2 of the License, or
; (at your option) any later version.

Unicode true

!define NAME "Gaphor"
!define ID "gaphor"
!define DESC "Modeling Tool"

!define WEBSITE "https://gaphor.readthedocs.io"

!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}"
!define INSTDIR_KEY "Software\${NAME}"
!define INSTDIR_VALUENAME "InstDir"

!define MUI_CUSTOMFUNCTION_GUIINIT custom_gui_init
!include "MUI2.nsh"
!include "FileFunc.nsh"

Name "${NAME} (${VERSION})"
OutFile "gaphor-LATEST.exe"
SetCompressor /SOLID /FINAL lzma
SetCompressorDictSize 32
InstallDir "$PROGRAMFILES\${NAME}"
RequestExecutionLevel admin

Var INST_BIN
Var UNINST_BIN

!define MUI_ABORTWARNING
!define MUI_ICON "gaphor.ico"

!insertmacro MUI_PAGE_LICENSE "gaphor\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Catalan"
!insertmacro MUI_LANGUAGE "Dutch"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "PortugueseBR"
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "Swedish"


Section "Install"
    SetShellVarContext all

    ; Use this to make things faster for testing installer changes
    ;~ SetOutPath "$INSTDIR\bin"
    ;~ File /r "mingw32\bin\*.exe"

    SetOutPath "$INSTDIR"
    File /r "*.*"

    StrCpy $INST_BIN "$INSTDIR\launch-gaphor.exe"
    StrCpy $UNINST_BIN "$INSTDIR\uninstall.exe"

    ; Store installation folder
    WriteRegStr HKLM "${INSTDIR_KEY}" "${INSTDIR_VALUENAME}" $INSTDIR

    ; Set up an entry for the uninstaller
    WriteRegStr HKLM "${UNINST_KEY}" \
        "DisplayName" "${NAME} - ${DESC}"
    WriteRegStr HKLM "${UNINST_KEY}" "DisplayIcon" "$\"$INST_BIN$\""
    WriteRegStr HKLM "${UNINST_KEY}" "UninstallString" \
        "$\"$UNINST_BIN$\""
    WriteRegStr HKLM "${UNINST_KEY}" "QuietUninstallString" \
    "$\"$UNINST_BIN$\" /S"
    WriteRegStr HKLM "${UNINST_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${UNINST_KEY}" "HelpLink" "${WEBSITE}"
    WriteRegStr HKLM "${UNINST_KEY}" "Publisher" "${NAME} Community"
    WriteRegStr HKLM "${UNINST_KEY}" "DisplayVersion" "${VERSION}"
    WriteRegDWORD HKLM "${UNINST_KEY}" "NoModify" 0x1
    WriteRegDWORD HKLM "${UNINST_KEY}" "NoRepair" 0x1
    ; Installation size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "${UNINST_KEY}" "EstimatedSize" "$0"

    ; Register a default entry for file extension
    WriteRegStr HKLM "Software\Classes\${NAME}.ModelFile\open\command" "" "$\"$INST_BIN$\""
    WriteRegStr HKLM "Software\Classes\${NAME}.ModelFile\DefaultIcon" "" "$\"$INST_BIN$\""

    ; Register supported file extension
    WriteRegStr HKLM "Software\Classes\.${ID}" ".gaphor" "${NAME}.ModelFile"

    ; Add application entry
    WriteRegStr HKLM "Software\${NAME}\${ID}\Capabilities" "ApplicationDescription" "${DESC}"
    WriteRegStr HKLM "Software\${NAME}\${ID}\Capabilities" "ApplicationName" "${NAME}"

    ; Register application entry
    WriteRegStr HKLM "Software\RegisteredApplications" "${NAME}" "Software\${NAME}\${ID}\Capabilities"

    ; Register app paths
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\App Paths\launch-gaphor.exe" "" "$INST_BIN"

    ; Create uninstaller
    WriteUninstaller "$UNINST_BIN"

    ; Create start menu shortcuts
    CreateDirectory "$SMPROGRAMS\${NAME}"
    CreateShortCut "$SMPROGRAMS\${NAME}\${NAME}.lnk" "$INST_BIN"
SectionEnd

Function custom_gui_init
    BringToFront

    ; Read the install dir and set it
    Var /GLOBAL instdir_temp
    Var /GLOBAL uninst_bin_temp

    SetRegView 32
    ReadRegStr $instdir_temp HKLM "${INSTDIR_KEY}" "${INSTDIR_VALUENAME}"
    SetRegView lastused
    StrCmp $instdir_temp "" skip 0
        StrCpy $INSTDIR $instdir_temp
    skip:

    SetRegView 64
    ReadRegStr $instdir_temp HKLM "${INSTDIR_KEY}" "${INSTDIR_VALUENAME}"
    SetRegView lastused
    StrCmp $instdir_temp "" skip2 0
        StrCpy $INSTDIR $instdir_temp
    skip2:

    StrCpy $uninst_bin_temp "$INSTDIR\uninstall.exe"

    ; try to un-install existing installations first
    IfFileExists "$INSTDIR" do_uninst do_continue
    do_uninst:
        ; instdir exists
        IfFileExists "$uninst_bin_temp" exec_uninst rm_instdir
        exec_uninst:
            ; uninstall.exe exists, execute it and
            ; if it returns success proceede, otherwise abort the
            ; installer (uninstall aborted by user for example)
            ExecWait '"$uninst_bin_temp" _?=$INSTDIR' $R1
            ; uninstall suceeded, since the uninstall.exe is still there
            ; goto rm_instdir as well
            StrCmp $R1 0 rm_instdir
            ; uninstall failed
            Abort
        rm_instdir:
            ; either the uninstaller was sucessfull or
            ; the uninstaller.exe wasn't found
            RMDir /r "$INSTDIR"
    do_continue:
        ; the instdir shouldn't exist from here on

    BringToFront
FunctionEnd

Section "Uninstall"
    SetShellVarContext all
    SetAutoClose true

    ; Remove start menu entries
    Delete "$SMPROGRAMS\${NAME}\${NAME}.lnk"
    RMDir "$SMPROGRAMS\${NAME}"

    ; Remove application registration and file assocs
    DeleteRegKey HKLM "Software\Classes\${NAME}.ModelFile"
    DeleteRegKey HKLM "Software\.${ID}"
    DeleteRegKey HKLM "Software\${NAME}"
    DeleteRegValue HKLM "Software\RegisteredApplications" "${NAME}"

    ; Remove app paths
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\App Paths\launch-gaphor.exe"

    ; Delete installation related keys
    DeleteRegKey HKLM "${UNINST_KEY}"
    DeleteRegKey HKLM "${INSTDIR_KEY}"

    ; Delete files
    RMDir /r "$INSTDIR"
SectionEnd
