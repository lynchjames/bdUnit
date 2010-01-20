#region Using Statements

using System.Collections.Generic;
using System.Linq;
using bdUnit.Core;
using bdUnit.Core.AST;
using bdUnit.Core.Extensions;
using bdUnit.Core.Templates;
using NUnit.Framework;

#endregion

namespace bdUnit.Tests.Base
{
    public class TestBase
    {
        protected Parser _parser;
        protected string _input;

        protected Constraint Constraint
        {
            get
            {
                return ((When) _parser.Parse().ElementAt(0).StatementList.ElementAt(0)).Constraints[0];
            }
        }

        public void CreateInputAndConfigure(string setupText, string testText, string concreteClass)
        {
            _input = CreateInput(setupText, testText, concreteClass);
            if (_parser == null)
            {
                _parser = new Parser(_input);
            }
            else
            {
                _parser.Input = _input;
            }
        }

        public string CreateInput(string setupText, string testText, string concreteClass)
        {
            var setup = setupText ?? string.Empty;
            var tests = testText ?? string.Empty;
            var inputs = new Dictionary<string, object> {{"setupContents", setup}, {"testContents", tests}, {"concreteClass", concreteClass}};
            return inputs.AsNVelocityTemplate(TemplateEnum.InputWrapper);
        }

        public void ParseTest()
        {
            var tests = _parser.Parse().ToList();
            Assert.IsNotEmpty(tests);
        }
    }
}