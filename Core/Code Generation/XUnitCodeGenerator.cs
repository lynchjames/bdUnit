﻿#region Using Statements

using System.Collections.Generic;
using bdUnit.Core.AST;

#endregion

namespace bdUnit.Core
{
    public class XUnitCodeGenerator
    {
        #region TextTemplates

        public readonly string TestFixtureText = ("#region Using Statements\nusing System.Collections.Generic;\nusing System.Diagnostics;\nusing bdUnit.Interfaces;\nusing Rhino.Mocks;\nusing StructureMap;\nusing Xunit;\nusing System;\n#endregion\n\nnamespace bdUnit.Interfaces \n{##interfaces##\n}\n\nnamespace bdUnit.Tests \n{\n\tpublic class ##fixturename##\n\t{\n##structuremap##\n##tests##\t}\n}").Replace("##structuremap##", StructureMap);

        public readonly string TestText = "\t\t[Fact]\n\t\tpublic void ##testname##()";

        public readonly string MethodText = "\t\t##returntype## ##methodname##(##params##);";

        public readonly string PropertyText = "\t\t##typename## ##propertyname## { get; set; }\n";

        public readonly string TypeText = "\n\n\tpublic partial interface I##typename##\n\t{\n##content##\t}";

        public readonly string AssertText = "\t\t\tAssert.True(##clause##);";

        public static readonly string StructureMap =
            @"        public void SetUpFixture()
        {
            ObjectFactory.Initialize(
            x => x.Scan(scanner =>
            {
                var location = AppDomain.CurrentDomain.BaseDirectory;
                scanner.AssembliesFromPath(location);
                scanner.WithDefaultConventions();
            }));
        }";

        #endregion

        public string GenerateTestFixture(List<Test> tests, string fileName)
        {
            var generator = new CodeGenerator(TestFixtureText, TestText, MethodText, PropertyText, TypeText,
                                                  AssertText);
            var code = generator.GenerateTestFixture(tests, fileName);
            generator = null;
            return code;
        }
    }
}
