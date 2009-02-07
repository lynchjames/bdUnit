#region Using Statements

using System.Collections.Generic;
using bdUnit.Core.AST;

#endregion

namespace bdUnit.Core
{
    public class XUnitCodeGenerator
    {
        #region TextTemplates

        public readonly string TestFixtureText = "#region Using Statements\nusing System.Collections.Generic;\nusing bdUnit.Interfaces;\nusing Rhino.Mocks;\nusing StructureMap;\nusing Xunit;\n#endregion\n\nnamespace bdUnit.Interfaces \n{##interfaces##\n}\n\nnamespace bdUnit.Tests \n{\n\tpublic class ##fixturename##\n\t{\n##tests##\t}\n}";

        public readonly string TestText = "\t\t[Fact]\n\t\tpublic void ##testname##()";

        public readonly string MethodText = "\t\t##returntype## ##methodname##(##params##);";

        public readonly string PropertyText = "\t\t##typename## ##propertyname## { get; set; }\n";

        public readonly string TypeText = "\n\n\t[PluginFamily(\"bdUnit\")]\n\tpublic interface I##typename##\n\t{\n##content##\t}";

        public readonly string AssertText = "\t\t\tAssert.IsTrue(##clause##);";

        #endregion

        public string GenerateTestFixture(List<Test> tests, string fileName)
        {
            var generator = new CodeGeneratorBase(TestFixtureText, TestText, MethodText, PropertyText, TypeText,
                                                  AssertText);
            return generator.GenerateTestFixture(tests, fileName);
        }
    }
}
