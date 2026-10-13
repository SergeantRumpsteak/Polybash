; Polybash - Online-Installer (Inno Setup 6.1 oder neuer)
;
; Ein Doppelklick auf Polybash-Installer.exe genuegt:
;   1. Das Spiel (spiel.py + Karten) steckt schon in der Datei und wird entpackt.
;   2. Ist auf dem Rechner kein passendes Python (3.9 - 3.12) vorhanden, wird Python 3.12 von python.org
;      heruntergeladen und nur fuer Polybash installiert (Unterordner "python", kein Admin, kein PATH-Eintrag).
;   3. Panda3D (die Spiele-Engine) wird per pip aus dem Internet geholt, in einer eigenen Umgebung ("venv").
;   4. Verknuepfungen im Startmenue (und optional auf dem Desktop) starten das Spiel.
;
; Bauen: build_online_installer.bat (auf einem Windows-PC mit Inno Setup) -> dist\Polybash-Installer.exe

#define AppVer "1.0"
#define PyUrl "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
#define PandaSpec "panda3d>=1.10.14,<1.11"

[Setup]
AppName=Polybash
AppVersion={#AppVer}
AppPublisher=Polybash
DefaultDirName={localappdata}\Polybash
DefaultGroupName=Polybash
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=Polybash-Installer
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName=Polybash
ArchitecturesInstallIn64BitMode=x64compatible
DisableWelcomePage=no

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "Verknuepfung auf dem Desktop anlegen"; GroupDescription: "Zusaetzliche Symbole:"

[Files]
Source: "..\spiel.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\maps\*"; DestDir: "{app}\maps"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "..\sounds\*"; DestDir: "{app}\sounds"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Icons]
Name: "{group}\Polybash"; Filename: "{app}\venv\Scripts\pythonw.exe"; Parameters: """{app}\spiel.py"""; WorkingDir: "{app}"
Name: "{group}\Polybash deinstallieren"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Polybash"; Filename: "{app}\venv\Scripts\pythonw.exe"; Parameters: """{app}\spiel.py"""; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\venv\Scripts\pythonw.exe"; Parameters: """{app}\spiel.py"""; WorkingDir: "{app}"; Description: "Polybash jetzt starten"; Flags: nowait postinstall skipifsilent; Check: InstallOk

[UninstallDelete]
Type: filesandordirs; Name: "{app}\venv"
Type: filesandordirs; Name: "{app}\python"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: files; Name: "{app}\install.log"

[Code]
var
  DownloadPage: TDownloadWizardPage;
  NeedPython: Boolean;
  SysPython: String;
  Ok: Boolean;

function InstallOk: Boolean;
begin
  Result := Ok;
end;

{ Fuehrt "cmd /C <Befehl>" aus und liefert den Rueckgabewert (-1 = konnte nicht gestartet werden). }
function RunCmd(const Args: String): Integer;
var
  RC: Integer;
begin
  if Exec(ExpandConstant('{cmd}'), '/C ' + Args, '', SW_HIDE, ewWaitUntilTerminated, RC) then
    Result := RC
  else
    Result := -1;
end;

{ Ruft ein Programm auf und haengt seine Ausgabe an install.log an (hilft bei der Fehlersuche). }
function RunLogged(const Exe, Params: String): Integer;
begin
  Result := RunCmd('""' + Exe + '" ' + Params + ' >> "' + ExpandConstant('{app}\install.log') + '" 2>&1"');
end;

{ Ist hinter dem Aufruf (z. B. "py -3.12") ein Python 3.9 - 3.12? Dann dessen Pfad, sonst ''. }
function TryPython(const Cmd: String): String;
var
  F: String;
  S: AnsiString;
begin
  Result := '';
  F := ExpandConstant('{tmp}\pyexe.txt');
  DeleteFile(F);
  if RunCmd(Cmd + ' -c "import sys; sys.exit(0 if (3,9) <= sys.version_info[:2] <= (3,12) else 1)" >nul 2>&1') <> 0 then
    Exit;
  if RunCmd(Cmd + ' -c "import sys; print(sys.executable)" > "' + F + '" 2>nul') <> 0 then
    Exit;
  if LoadStringFromFile(F, S) then
  begin
    Result := Trim(String(S));
    if not FileExists(Result) then
      Result := '';
  end;
end;

function FindPython: String;
begin
  Result := TryPython('py -3.12');
  if Result = '' then Result := TryPython('py -3.11');
  if Result = '' then Result := TryPython('py -3.10');
  if Result = '' then Result := TryPython('py -3.9');
  if Result = '' then Result := TryPython('python');
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpReady then
  begin
    SysPython := FindPython;
    NeedPython := SysPython = '';
    if NeedPython then
    begin
      DownloadPage.Clear;
      DownloadPage.Add('{#PyUrl}', 'python-installer.exe', '');
      DownloadPage.Show;
      try
        try
          DownloadPage.Download;
        except
          if not DownloadPage.AbortedByUser then
            SuppressibleMsgBox('Python konnte nicht heruntergeladen werden:' + #13#10 + GetExceptionMessage + #13#10#13#10 +
              'Bitte pruefe die Internetverbindung und starte den Installer noch einmal.', mbCriticalError, MB_OK, IDOK);
          Result := False;
        end;
      finally
        DownloadPage.Hide;
      end;
    end;
  end;
end;

function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo, MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
begin
  Result := MemoDirInfo + NewLine + NewLine +
    'Beim Installieren wird (falls noetig) Python 3.12 von python.org und die Spiele-Engine Panda3D aus dem Internet geladen.' + NewLine +
    'Das dauert je nach Verbindung 2 bis 5 Minuten - bitte das Fenster offen lassen.';
  if MemoTasksInfo <> '' then
    Result := Result + NewLine + NewLine + MemoTasksInfo;
end;

procedure Fail(const Msg: String);
begin
  Ok := False;
  MsgBox(Msg + #13#10#13#10 + 'Details stehen in:' + #13#10 + ExpandConstant('{app}\install.log'), mbError, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Prog: TOutputMarqueeProgressWizardPage;
  App, Py, VenvPy: String;
  RC: Integer;
begin
  if CurStep <> ssPostInstall then
    Exit;
  Ok := False;
  App := ExpandConstant('{app}');
  VenvPy := App + '\venv\Scripts\python.exe';
  Prog := CreateOutputMarqueeProgressPage('Polybash wird eingerichtet', 'Bitte warten - das Fenster offen lassen.');
  try
    Prog.Show;
    if NeedPython then
    begin
      Prog.SetText('Python 3.12 wird installiert ...', 'nur fuer Polybash, ohne Administratorrechte');
      Prog.Animate;
      RC := RunCmd('""' + ExpandConstant('{tmp}\python-installer.exe') + '" /quiet InstallAllUsers=0 PrependPath=0 ' +
        'Include_launcher=0 Include_test=0 Include_doc=0 Include_pip=1 Shortcuts=0 AssociateFiles=0 ' +
        'TargetDir="' + App + '\python"" >> "' + App + '\install.log" 2>&1');
      Py := App + '\python\python.exe';
      if ((RC <> 0) and (RC <> 3010)) or not FileExists(Py) then
      begin
        Fail('Die Installation von Python ist fehlgeschlagen (Code ' + IntToStr(RC) + ').');
        Exit;
      end;
    end
    else
      Py := SysPython;

    Prog.SetText('Eigene Umgebung wird angelegt ...', '');
    Prog.Animate;
    RC := RunLogged(Py, '-m venv "' + App + '\venv"');
    if (RC <> 0) or not FileExists(VenvPy) then
    begin
      Fail('Die Python-Umgebung konnte nicht angelegt werden (Code ' + IntToStr(RC) + ').');
      Exit;
    end;

    Prog.SetText('Spiele-Engine Panda3D wird heruntergeladen und installiert ...', 'das dauert etwa 1 bis 3 Minuten');
    Prog.Animate;
    RC := RunLogged(VenvPy, '-m pip install --disable-pip-version-check --no-warn-script-location "{#PandaSpec}"');
    if RC <> 0 then
    begin
      Fail('Panda3D konnte nicht installiert werden (Code ' + IntToStr(RC) + '). Ist der Rechner mit dem Internet verbunden?');
      Exit;
    end;
    Ok := True;
  finally
    Prog.Hide;
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if (CurPageID = wpFinished) and (not Ok) then
    WizardForm.FinishedLabel.Caption := 'Die Einrichtung ist nicht vollstaendig abgeschlossen. ' +
      'Bitte den Installer noch einmal ausfuehren. Die Meldung steht in install.log im Installationsordner.';
end;
