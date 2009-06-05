rem This batch file can be used to compile the Simple.mg file into Simple.mx, which
rem can then be loaded by DynamicParser.
@echo off
"C:\Program Files\Microsoft Oslo SDK 1.0\Bin\mgx.exe" bdUnitMGrammar.mg
pause
-?