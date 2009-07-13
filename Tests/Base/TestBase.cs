#region Using Statements

using System.Collections.Generic;
using bdUnit.Core;
using bdUnit.Core.Extensions;
using bdUnit.Core.Templates;

#endregion

namespace bdUnit.Tests.Base
{
    public class TestBase
    {
        protected Parser _parser;

        public void Configure(string input)
        {
            _parser = new Parser(input);
        }

        public string CreateInput(string setupText, string testText)
        {
            var setup = setupText ?? string.Empty;
            var tests = testText ?? string.Empty;
            var inputs = new Dictionary<string, object> {{"setup-contents", setup}, {"test-contents", tests}};
            return inputs.AsNVelocityTemplate(TemplateEnum.InputWrapper);
        }
    }
}