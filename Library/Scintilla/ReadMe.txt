ScintillaNet 2.0
-----------------
This version of ScintillaNET will work with Visual Studio 2005 and 2008 including express editions. ScintillaNET relies on the unmanaged dll SciLexer.dll. If ScintillaNET can't find this dll you will get "Window class name is not valid" exceptions and basically nothing will work. My suggestion is to copy SciLexer.dll to your \Windows\System32 folder on the development PC. When deploying your software, this isn't necessary. Instead just make sure SciLexer.dll is in the same folder as ScintillaNet.dll.

Then to get started:
	Open Visual Studio and create or open a Windows Forms Project. 
	Go to the design view of a form. 
	Right click on the Toolbox window and select "Choose Items". 
	From the ".NET Framework Components" tab click the "Browse..." button
	Locate and select the ScintillaNet.dll assembly.
	Ensure the "Scintilla" component is Checked
	Click OK
	Drag a new Scintilla control onto the design surface