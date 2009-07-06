#region Using Statements

using System.Collections.Generic;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;
using bdUnit.Core.Extensions;
using bdUnit.Core.Generators;
using bdUnit.Core.Templates;

#endregion

namespace bdUnit.Core
{
    public class CodeGenerator : GeneratorBase, ICodeGenerator
    {
        private readonly IMethodSignatureGenerator _methodSignatureGenerator;
        private readonly IPropertyGenerator _propertGenerator;
        public IAssertGenerator _assertGenerator;
        public IInterfaceGenerator _interfaceGenerator;
        public IMethodGenerator _methodGenerator;

        public CodeGenerator(TemplateEnum fixtureTemplate, string testText, string methodText, string propertyText,
                             string typeText, string assertText)
        {
            var access = AccessEnum.@public;
            TestFixtureTemplate = fixtureTemplate;
            TestText = testText;
            MethodText = methodText;
            PropertyText = propertyText;
            TypeText = typeText;
            AssertText = assertText;
            _assertGenerator = new AssertGenerator(assertText);
            _methodGenerator = new MethodGenerator(_assertGenerator, testText);
            _methodSignatureGenerator = new MethodSignatureGenerator(access, methodText);
            _propertGenerator = new PropertyGenerator(access, propertyText);
            _interfaceGenerator = new InterfaceGenerator(access, typeText, _methodSignatureGenerator, _propertGenerator);
        }

        #region ICodeGenerator Members

        public string GenerateTestFixture(List<Test> tests, string fileName)
        {
            var stringBuilder = new StringBuilder();
            var count = tests.Count;
            var templateInputs = new Dictionary<string, object>();
            for (var i = 0; i < count; i++)
            {
                stringBuilder.Append(GenerateTest(tests[i], "", AccessEnum.@public));
                var typeList = tests[i].TypeList;
                var typeCount = typeList.Count;
                if (tests[i].TypeList != null && typeCount > 0)
                {
                    var interfaceText = new StringBuilder();
                    for (var j = 0; j < typeCount; j++)
                    {
                        interfaceText.Append(_interfaceGenerator.Generate(typeList[j]));
                    }
                    templateInputs.Add("interfaces", interfaceText.ToString());
                }
                else
                {
                    templateInputs.Add("interfaces", string.Empty);
                }
            }
            //testFixture = testFixture.Replace("##fixturename##", tests[0].Title);
            //testFixture = testFixture.Replace("##tests##", stringBuilder.ToString());
            templateInputs.Add("testTitle", tests[0].Title);
            templateInputs.Add("tests", stringBuilder.ToString());
            return templateInputs.AsNVelocityTemplate(TestFixtureTemplate);
        }

        public string GenerateTest(Test test, string path, AccessEnum access)
        {
            var stringBuilder = new StringBuilder();
            Access = access;
            var statementList = test.StatementList;
            stringBuilder = _methodGenerator.Generate(statementList, stringBuilder);
            return stringBuilder.ToString();
        }

        #endregion
    }
}