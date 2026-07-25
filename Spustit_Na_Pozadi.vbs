Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strScriptPath = fso.GetParentFolderName(WScript.ScriptFullName) & "\src"
WshShell.CurrentDirectory = strScriptPath
WshShell.Run "python main.py --headless", 0, False
