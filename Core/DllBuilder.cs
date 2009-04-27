#region Using Statements

using System;
using System.CodeDom.Compiler;
using System.Collections.Generic;
using System.IO;
using System.Text;
using bdUnit.Core.Enum;
using bdUnit.Core.Extensions;
using bdUnit.Core.Templates;
using Microsoft.CSharp;

#endregion

namespace bdUnit.Core
{
    public class DllBuilder
    {
        private readonly Parser _parser;

        private readonly string[] References =
            new[]
                {
                    "Rhino.Mocks", "nunit.core", "nunit.core.interfaces", "nunit.framework",
                    "xunit", "MbUnit.Framework", "StructureMap", "StructureMap.AutoMocking"
                };

        public DllBuilder(Parser parser)
        {
            _parser = parser;
        }

        public string CompileDll(string[] filePaths, UnitTestFrameworkEnum currentFramework)
        {
            CodeDomProvider compiler = new CSharpCodeProvider(new Dictionary<string, string>
                                                                  {
                                                                      {"CompilerVersion", "v3.5"}
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
                return "Successfully Generated Dll";
            }
            catch (Exception ex)
            {
                throw ex;
                return "One or more documents could not be parsed. Please check and try again. Exception: " + ex.Message;
            }
        }

        private string[] GetSource(string[] filePaths, UnitTestFrameworkEnum framework)
        {
            var source = new List<string>();
            for (var i = 0; i < filePaths.Length; i++)
            {
                if (filePaths[i] == null) continue;

                _parser.Input = File.ReadAllText(filePaths[i]);
                source.Add(_parser.Parse(framework));
            }
            source.Add(NVelocityCodeGenerationExtensions.GetNVelocityTemplate(TemplateEnum.StructureMapInitialization));
            
            return source.ToArray();
        }
    }
}