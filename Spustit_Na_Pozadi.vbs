Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strScriptPath = fso.GetParentFolderName(WScript.ScriptFullName) & "\src"
WshShell.CurrentDirectory = strScriptPath

' Run python headless check silently (0 = hidden window) and wait for completion (True)
WshShell.Run "python main.py --headless", 0, True

' Display brief 3-second notification popup
WshShell.Popup "Kontrola na pozadí byla úspěšně dokončena." & vbCrLf & "Výsledky byly uloženy do databáze a aplikace.", 4, "Update Seeker", 64
