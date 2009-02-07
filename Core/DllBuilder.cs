using System;
using System.CodeDom.Compiler;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using bdUnit.Core;
using Core.Enum;
using Microsoft.CSharp;

namespace bdUnit.Core
{
    public class DllBuilder
    {
        private string[] References = new[]
                                          {
                                              "Rhino.Mocks", "nunit.core", "nunit.core.interfaces", "nunit.framework",
                                              "StructureMap", "StructureMap.AutoMocking"
                                          };
      
        public void CompileDll(string folderPath)
        {
            CodeDomProvider compiler = new CSharpCodeProvider(new Dictionary<string, string> {{"CompilerVersion","v3.5"}});
            var compilerParameters = new CompilerParameters
                                         {
                                             GenerateInMemory = false,
                                             GenerateExecutable = false,
                                             IncludeDebugInformation = true,
                                             OutputAssembly = "bdUnit.dll"
                                         };
            foreach (var reference in References)
            {
                compilerParameters.ReferencedAssemblies.Add(AppDomain.CurrentDomain.BaseDirectory + "\\" + string.Format("{0}.dll", reference));
            }
            compilerParameters.ReferencedAssemblies.Add("System.dll");
            var source = GetSource(folderPath, UnitTestFrameworkEnum.NUnit);
            var results = compiler.CompileAssemblyFromSource(compilerParameters, source);
        }

        private string[] GetSource(string folderPath, UnitTestFrameworkEnum framework)
        {
            Directory.SetCurrentDirectory(folderPath);
            var directory = Directory.GetCurrentDirectory();
            var files = Directory.GetFiles(folderPath, "*.input");
            string[] source = new string[files.Length];
            for (var i = 0; i < files.Length; i++)
            {
                var paths = new Dictionary<string, string>();
                paths.Add("input", string.Format("{0}", files[i]));
                paths.Add("grammar", "/Development/bdUnit/Core/Grammar/TestWrapper.mg");
                var parser = new Parser(paths);
                source[i] = parser.Parse(framework);
            }
            Debug.Write(source.ToString());
            return source;
        }
    }
}
