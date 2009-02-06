#region Using Statements

using System.Collections.Generic;
using System.Linq;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;
using bdUnit.Core.Utility;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;
using bdUnit.Core.Utility;
using Core.Enum;

#endregion

namespace bdUnit.Core
{
    public class NUnitCodeGenerator
    {
        #region TextTemplates

        public readonly string TestFixtureText = "#region Using Statements\nusing System.Collections.Generic;\nusing bdUnit.Interfaces;\nusing NUnit.Framework;\nusing Rhino.Mocks;\nusing StructureMap;\n#endregion\n\nnamespace bdUnit.Interfaces \n{##interfaces##\n}\n\nnamespace bdUnit.Tests \n{\n\t[TestFixture]\n\tpublic class ##fixturename##\n\t{\n##tests##\t}\n}";

        public readonly string TestText = "\n\t\t[Test]\n\t\tpublic void ##testname##()";

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