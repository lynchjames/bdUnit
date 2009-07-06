#region Using Statements

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using bdUnit.Core;
using bdUnit.Core.Enum;
using bdUnit.Core.Utility;
using NUnit.Framework;

#endregion

namespace bdUnit.Tests
{
    [TestFixture]
    public class Parsing
    {
        [Test]
        public void Incremental_Parsed_But_Fails_To_Map_To_AST1()
        {
            IncrementalParse(200,300);
        }

        [Test]
        public void Incremental_Parsed_But_Fails_To_Map_To_AST2()
        {
            IncrementalParse(400, 500);
        }

        [Test]
        public void Incremental_Parsed_But_Fails_To_Map_To_AST3()
        {
            IncrementalParse(1000, 1100);
        }

        [Test]
        public void Incremental_Parsed_But_Fails_To_Map_To_AST4()
        {
            IncrementalParse(2000, 2100);
        }

        private void IncrementalParse(int start, int end)
        {
            var input = File.ReadAllText("../../Input Files/Incremental/LogansRun_Wrapper.bdunit");
            var setupText = File.ReadAllText("../../Input Files/Incremental/LogansRun_Setup.bdunit");
            var testText = File.ReadAllText("../../Input Files/Incremental/LogansRun_Tests.bdunit");
            var setupCharacters = setupText.ToCharArray();
            var testCharacters = testText.ToCharArray();
            var setupCount = setupCharacters.Length;
            var testCount = testCharacters.Length;
            var setupInput = string.Empty;
            var testInputs = new List<string>();
            for (var i = 0; i < setupCount; i++)
            {
                setupInput = string.Concat(setupInput, setupCharacters[i]);
                testInputs.Add(input.Replace("##setup-contents##", setupInput).Replace("##test-contents##", string.Empty));
            }
            var testInput = string.Empty;
            for (var i = 0; i < testCount; i++)
            {
                testInput = string.Concat(testInput, testCharacters[i]);
                testInputs.Add(input.Replace("##setup-contents##", string.Empty).Replace("##test-contents##", testInput));
            }
            var total = testInputs.Count;
            for (var i = start; i < end; i++)
            {
                var testInputToParse = testInputs[i];
                try
                {
                    Debug.WriteLine(string.Format("Parsing and Converting {0} of {1}", i+1, total));
                    var parser = new Parser(testInputToParse);
                    parser.Parse(UnitTestFrameworkEnum.NUnit);
                    Debug.WriteLine(string.Format("Successfully Parsed and Converted {0} of {1}", i + 1, total));
                }
                catch (Exception ex)
                {
                    if (!(ex is DynamicParserExtensions.ParserErrorException))
                    {
                        Debug.WriteLine(string.Format("Parse {0} of {1} Passed But AST Mapping Failed \nReason: {2}", i + 1, total, ex.Message));
                    }
                }
            }
        }
    }
}