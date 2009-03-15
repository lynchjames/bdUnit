#region Using Statements

using System.Collections.Generic;
using bdUnit.Core.AST;

#endregion

namespace bdUnit.Core
{
    public class MbUnitCodeGenerator
    {
        #region TextTemplates

        public readonly string TestFixtureText = ("#region Using Statements\nusing System.Collections.Generic;\nusing System.Diagnostics;\nusing bdUnit.Interfaces;\nusing Rhino.Mocks;\nusing StructureMap;\nusing MbUnit.Framework;\nusing System;\n#endregion\n\nnamespace bdUnit.Interfaces \n{##interfaces##\n}\n\nnamespace bdUnit.Tests \n{\n\t[TestFixture]\n\t[FixtureCategory(\"BDD Tests\")]\n\tpublic class ##fixturename##\n\t{\n##structuremap##\n##tests##\t}\n}").Replace("##structuremap##", StructureMap);

        public readonly string TestText = "\t\t[Test]\n\t\tpublic void ##testname##()";

        public readonly string MethodText = "\t\t##returntype## ##methodname##(##params##);";

        public readonly string PropertyText = "\t\t##typename## ##propertyname## { get; set; }\n";

        public readonly string TypeText = "\n\n\t[PluginFamily(\"bdUnit\")]\n\tpublic partial interface I##typename##\n\t{\n##content##\t}";

        public readonly string AssertText = "\t\t\tAssert.IsTrue(##clause##);";

        public static readonly string StructureMap =
            @"      [TestFixtureSetUp]
        public void Setup()
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
