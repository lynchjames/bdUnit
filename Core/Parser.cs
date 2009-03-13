#region Using Statements

using System;
using System.Collections.Generic;
using System.Dataflow;
using System.Diagnostics;
using System.IO;
using System.Xml.Linq;
using bdUnit.Core.AST;
using bdUnit.Core.Utility;
using Core.Enum;
using Microsoft.M.Grammar;
using Type=bdUnit.Core.AST.Type;

#endregion

namespace bdUnit.Core
{
    public class Parser : IDisposable
    {
        private Dictionary<Identifier, Type> explicitTypeMappings = new Dictionary<Identifier, Type>();
        private Dictionary<Identifier, Type> labelToTypeMappings;
        private List<Pair<XNamespace, string>> namespaces = new List<Pair<XNamespace, string>>();
        private DynamicParser parser;

        public Parser(string input, string grammar)
        {
            Grammar = grammar;
            Input = input;
        }

        public Parser(string input)
        {
            Grammar = File.ReadAllText(Settings.GrammarPath);
            Input = input;
        }

        public Parser(string input, IDictionary<string, string> grammarPath)
        {
            Input = input;
            var grammar = File.ReadAllText(grammarPath["grammar"]);
            Grammar = grammar;
        }

        public Parser(IDictionary<string, string> filePaths)
        {
            var stringInput = File.ReadAllText(filePaths["input"]);
            Input = stringInput;
            var grammar = File.ReadAllText(filePaths["grammar"]);
            Grammar = grammar;
            var pathParts = filePaths["input"].Split(new[] {'/'});
            TestFileName = pathParts[pathParts.Length - 1].Replace(".input", string.Empty);
            TestFileName = TestFileName.Insert(TestFileName.Length, ".cs");
        }

        public static string InputPath { get; set; }
        public static string TestFileName { get; set; }
        public static string GrammarPath { get; set; }
        public static string Grammar { get; set; }
        public string Input { get; set; }

        public static DynamicParser LoadGrammar()
        {
            var errorReporter = ErrorReporter.Standard;

            var compiler = new MGrammarCompiler
                               {
                                   SourceItems = new[]
                                                     {
                                                         new SourceItem
                                                             {
                                                                 Name = TestFileName ?? "Preview",
                                                                 ContentType = GContentType.Mg,
                                                                 TextReader = new StringReader(Grammar)
                                                             },
                                                     },
                               };
            compiler.References = new[] {"Languages", "Microsoft.Languages"};

            if (compiler.Compile(errorReporter) != 0 || errorReporter.HasErrors)
            {
                compiler = null;
                return null;
            }

            var dynamicParser = new DynamicParser();
            compiler.LoadDynamicParser(dynamicParser);
            compiler = null;
            return dynamicParser;
        }

        public string Parse(UnitTestFrameworkEnum framework)
        {
            
            var parser = LoadGrammar();
            var deserializer = new Deserializer();

            object root;
            var reporter = new DynamicParserExtensions.ExceptionErrorReporter();

            if (Input != null)
            {
                root = parser.ParseObject(new StringReader(Input), reporter);
            }
            else
            {
                root = parser.ParseObject(InputPath, reporter);
            }

            var tests = deserializer.Deserialize(root) as IList<object>;
            parser = null;
            deserializer = null;
            var list = new List<Test>();
            if (tests != null)
            {
                foreach (var test in tests)
                {
                    list.Add((Test)test);
                }
                switch (framework)
                {
                    case UnitTestFrameworkEnum.NUnit:
                        var nUnit = new NUnitCodeGenerator();
                        return nUnit.GenerateTestFixture(list, TestFileName);
                    case UnitTestFrameworkEnum.XUnit:
                        var xUnit = new XUnitCodeGenerator();
                        return xUnit.GenerateTestFixture(list, TestFileName);
                    case UnitTestFrameworkEnum.MbUnit:
                        var mbUnit = new MbUnitCodeGenerator();
                        return mbUnit.GenerateTestFixture(list, TestFileName);
                }
            }
            return string.Empty;
        }

        public void DoWork()
        {
            var parser = LoadGrammar();
            var deserializer = new Deserializer();

            object root;

            if (Input != null)
            {
                root = parser.ParseObject(new StringReader(Input), ErrorReporter.Standard);
            }
            else
            {
                root = parser.ParseObject(InputPath, ErrorReporter.Standard);
            }

            var tests = deserializer.Deserialize(root) as IList<object>;
            var list = new List<Test>();
            var codegen = new NUnitCodeGenerator();
            foreach (var test in tests)
            {
                list.Add((Test)test);
            }
            Debug.Write(codegen.GenerateTestFixture(list, TestFileName));
            //codegen.GenerateTest(test, "../../../Core/Inputs/LogansRunTest.cs", AccessEnum.@public);
        }

        public static void Main()
        {
        }

        public void Dispose()
        {
            Input = null;
            parser = null;
            namespaces = null;
            explicitTypeMappings = null;
            labelToTypeMappings = null;
        }
    }
}