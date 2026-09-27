' ==============================================================================
' Satyameva Aegis - Silent Native Desktop Application Launcher
' ==============================================================================
' Launches the Satyameva local blockchain node silently in the background
' (zero black command prompt popup) and opens the application in clean,
' frameless native app window mode using Chrome or Edge.
' ==============================================================================

Option Explicit

Dim fso, shell, currentDir, pythonCmd, appUrl, browserExe

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
appUrl = "http://127.0.0.1:5000/login"

' Function to check if HTTP endpoint is live
Function IsServerLive(url)
    On Error Resume Next
    Dim http
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    http.setTimeouts 1000, 1000, 1000, 2000
    http.Open "GET", url, False
    http.Send
    If Err.Number = 0 And (http.Status = 200 Or http.Status = 302) Then
        IsServerLive = True
    Else
        IsServerLive = False
    End If
    On Error GoTo 0
End Function

' 1. Check if server is already running; if not, launch it silently in background
If Not IsServerLive("http://127.0.0.1:5000/login") Then
    ' Run python run.py hidden (windowStyle = 0)
    shell.CurrentDirectory = currentDir
    shell.Run "cmd /c python run.py", 0, False

    ' Wait up to 8 seconds for the Flask server to initialize
    Dim attempts
    attempts = 0
    Do While attempts < 16 And Not IsServerLive("http://127.0.0.1:5000/login")
        WScript.Sleep 500
        attempts = attempts + 1
    Loop
End If

' 2. Locate Google Chrome or Microsoft Edge for frameless Native App Mode
Function GetAppBrowser()
    Dim paths, p, expanded
    paths = Array(_
        "%ProgramFiles%\Google\Chrome\Application\chrome.exe",_
        "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",_
        "%LocalAppData%\Google\Chrome\Application\chrome.exe",_
        "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",_
        "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"_
    )
    For Each p In paths
        expanded = shell.ExpandEnvironmentStrings(p)
        If fso.FileExists(expanded) Then
            GetAppBrowser = expanded
            Exit Function
        End If
    Next
    GetAppBrowser = ""
End Function

browserExe = GetAppBrowser()

' 3. Launch in standalone application window mode
If browserExe <> "" Then
    shell.Run """" & browserExe & """ --app=" & appUrl & " --window-size=1380,880", 1, False
Else
    ' Fallback to system default browser
    shell.Run appUrl, 1, False
End If
