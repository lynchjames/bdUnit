#region Using Statements

using System;
using System.CodeDom.Compiler;
using System.Collections.Generic;
using System.Text;
using Core.Enum;
using Microsoft.CSharp;

#endregion

namespace bdUnit.Core
{
    public class DllBuilder
    {
        private readonly string[] References = 
            new[]   {
                        "Rhino.Mocks", "nunit.core", "nunit.core.interfaces", "nunit.framework",
                        "xunit", "MbUnit.Framework", "StructureMap", "StructureMap.AutoMocking"
                    };
      
        public string CompileDll(string[] filePaths, UnitTestFrameworkEnum currentFramework)
        {
            CodeDomProvider compiler = new CSharpCodeProvider(new Dictionary<string, string>
                                                                    {
                                                                        {"CompilerVersion","v3.5"}
                                                                    });
            
            var parameters = new CompilerParameters
                             {
                                 GenerateInMemory = false,
                                 GenerateExecutable = false,
                                 IncludeDebugInformation = true,
                                 OutputAssembly = string.Format("bdUnit_{0}.dll", currentFramework),
                                 ReferencedAssemblies = {"System.dll"}
                             };
            
            foreach (var reference in References)
            {
                parameters.ReferencedAssemblies.Add(AppDomain.CurrentDomain.BaseDirectory
                                                            + string.Format("\\{0}.dll", reference));
            }
            try
            {
                var source = GetSource(filePaths, currentFramework);
                var results = compiler.CompileAssemblyFromSource(parameters, source);

                if (results.Errors.HasErrors)
                {
                    var errorText = new StringBuilder();
                    var count = results.Errors.Count;
                    for (var i = 0; i < count; i++)
                    {
                        errorText.AppendLine("Compilation Error: " + results.Errors[i].ErrorText);
                    }
                    return errorText.ToString();
                }
                return "Succesfully Generated Dll";
            }
            catch (Exception)
            {
                return "One or more documents could not be parsed. Please check and try again.";
            }
        }

        private static string[] GetSource(string[] filePaths, UnitTestFrameworkEnum framework)
        {
            var source = new string[filePaths.Length];
            for (var i = 0; i < filePaths.Length; i++)
            {
                var paths = new Dictionary<string, string>
                                {
                                    {"input", string.Format("{0}", filePaths[i])},
                                    {"grammar", Settings.GrammarPath}
                                };
                var parser = new Parser(paths);
                source[i] = parser.Parse(framework);
            }
            return source;
        }
    }
}