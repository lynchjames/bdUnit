#region Using Statements

using System;
using System.Collections.Generic;
using System.Dataflow;
using System.IO;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;
using bdUnit.Core.Utility;
using Microsoft.M.Grammar;

#endregion

namespace bdUnit.Core
{
    public class Parser : IDisposable
    {
        #region Properties

        private DynamicParser _parser;
        private bool IsGrammarLoaded;
        public string InputPath { get; set; }
        public string TestFileName { get; set; }
        private string Grammar { get; set; }
        public string Input { get; set; }

        #endregion

        #region Constructor

        public Parser()
        {
        }

        public Parser(string input)
        {
            Input = input;
        }

        public Parser(IDictionary<string, string> filePaths)
        {
            var stringInput = File.ReadAllText(filePaths["input"]);
            Input = stringInput;
            var pathParts = filePaths["input"].Split(new[] {'/'});
            TestFileName = pathParts[pathParts.Length - 1].Replace(".input", string.Empty);
            TestFileName = TestFileName.Insert(TestFileName.Length, ".cs");
        }

        #endregion

        #region IDisposable Members

        public void Dispose()
        {
            Input = null;
        }

        #endregion

        public void LoadGrammar()
        {
            var errorReporter = ErrorReporter.Standard;
            Grammar = Settings.MGrammar;
            var compiler = new MGrammarCompiler
                               {
                                   SourceItems = new[]
                                                     {
                                                         new SourceItem
                                                             {
                                                                 Name = TestFileName ?? "Preview",
                                                                 ContentType = ContentType.Mg,
                                                                 TextReader = new StringReader(Grammar)
                                                             }
                                                     }
                               };

            if (compiler.Compile(errorReporter) != 0 || errorReporter.HasErrors)
            {
                compiler = null;
                return;
            }

            var dynamicParser = new DynamicParser();
            compiler.LoadDynamicParser(dynamicParser);
            compiler = null;
            _parser = dynamicParser;
        }

        public string Parse(UnitTestFrameworkEnum framework)
        {
            if (!IsGrammarLoaded)
            {
                LoadGrammar();
                IsGrammarLoaded = true;
            }
            var deserializer = new Deserializer();

            var reporter = new DynamicParserExtensions.ExceptionErrorReporter();

            var root = Input != null
                              ? _parser.Parse<object>(null, new StringReader(Input), reporter)
                              : _parser.Parse<object>(InputPath, new StringReader(File.ReadAllText(InputPath)), reporter);
            var tests = deserializer.Deserialize(root) as IList<object>;
            var list = new List<Test>();
            if (tests != null)
            {
                foreach (var test in tests)
                {
                    list.Add((Test) test);
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
    }
}