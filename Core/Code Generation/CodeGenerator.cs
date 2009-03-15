﻿#region Using Statements

using System.Collections.Generic;
using System.Linq;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;
using bdUnit.Core.Generators;
using bdUnit.Core.Utility;
using bdUnit.Core.Enum;
using Type=bdUnit.Core.AST.Type;

#endregion

namespace bdUnit.Core
{
    public class CodeGenerator : GeneratorBase, ICodeGenerator
    {
        public IAssertGenerator _assertGenerator;
        public IMethodGenerator _methodGenerator;
        public IInterfaceGenerator _interfaceGenerator;
        private readonly IMethodSignatureGenerator _methodSignatureGenerator;
        private readonly IPropertyGenerator _propertGenerator;

        public CodeGenerator(string fixtureText, string testText, string methodText, string propertyText, string typeText, string assertText)
        {
            var access = AccessEnum.@public;
            TestFixtureText = fixtureText;
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

        public string GenerateTestFixture(List<Test> tests, string fileName)
        {
            var stringBuilder = new StringBuilder();
            var count = tests.Count;
            var testFixture = "";
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
                    testFixture = TestFixtureText.Replace("##interfaces##", interfaceText.ToString());
                }
                else
                {
                    testFixture = TestFixtureText.Replace("##interfaces##", "");
                }
            }
            testFixture = testFixture.Replace("##fixturename##", tests[0].Title);
            testFixture = testFixture.Replace("##tests##", stringBuilder.ToString());
            return testFixture;
        }

        public string GenerateTest(Test test, string path, AccessEnum access)
        {
            var stringBuilder = new StringBuilder();
            Access = access;
            var statementList = test.StatementList;
            stringBuilder = _methodGenerator.Generate(statementList, stringBuilder);
            return stringBuilder.ToString();
        }
    }
}