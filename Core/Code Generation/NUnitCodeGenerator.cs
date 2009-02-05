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

#endregion

namespace bdUnit.Core
{
    public class NUnitCodeGenerator : ICodeGenerator
    {
        public int InstanceIdentifier = 1;
        public AccessEnum Access { get; set; }

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
                        interfaceText.Append(GenerateInterfaces(typeList[j]));
                    }
                    testFixture = TestFixtureText.Replace("##interfaces##", interfaceText.ToString());
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
            stringBuilder = GenerateMethods(statementList, stringBuilder);
            
            //StreamWriter stream = File.CreateText(string.Format("{0}\\{1}.cs", path, test.Title));
            //stream.Write("");
            return stringBuilder.ToString();
        }

        public StringBuilder GenerateMethods(IList<IStatement> statements, StringBuilder stringBuilder)
        {
            var statementCount = statements.Count;
            if (statementCount > 0)
            {
                for (var i = 0; i < statementCount; i++)
                {
                    var statement = statements[i];
                    var method = statement.TargetMethod;
                    //list[i].TargetMethod.Loop.Constraints.ElementAt(0).Property
                    var when = new When();
                    if (statement.GetType() == when.GetType())
                    {
                        var count = method.Objects.Count;
                        for (var j = 0; j < count - 1; j++)
                        {
                            var objects = method.Objects;
                            var obj = objects[j];
                            var otherObj = objects[j == 0 ? 1 : 0];
                            var variables = string.Empty;
                            variables += string.Format("\t\t\tvar {0} = new {1};\n", obj.Instance, obj.Name);
                            variables += string.Format("\t\t\tvar {0} = new {1};\n", otherObj.Instance, otherObj.Name);
                            var methodUsage = string.Format("\t\t\t{0}.{1}({2});\n", obj.Instance, method.Name, otherObj.Instance);

                            //TODO: Add logic to determine type constuctor @User(Name = Jim, Age = 25) should correspond to var Jim = new User() {Name = "Jim", Age = 25};
                            var title = string.Format("When_{0}_{1}_{2}", obj.Name, method.Name, otherObj.Name);
                            stringBuilder.AppendLine(TestText.Replace("##testname##", title));
                            stringBuilder.AppendLine("\t\t{");
                            stringBuilder.Append(variables).Append(methodUsage);
                            if (method.Loop != null)
                            {
                                stringBuilder.Append(GenerateAsserts(obj, method.Loop.Constraints));
                            }
                            else if (method.Constraints.Count > 0)
                            {
                                for (var k = 0; k < method.Constraints.Count; k++)
                                {
                                    var constraint = method.Constraints[k];
                                    stringBuilder.Append(GenerateAsserts(constraint.Property.Object, new List<Constraint>(){constraint}));
                                }
                            }
                            stringBuilder.AppendLine("\t\t}");
                        }
                    }
                }
            }
            return stringBuilder;
        }

        public string GenerateInterfaces(Type type)
        {
            var wrapper = TypeText.Replace("##accesslevel##", Access.ToString()).Replace("##typename##",
                                                                                            type.Object.Name);
            var properties = type.PropertyList;
            var content = new StringBuilder();
            content.Append(GenerateProperties(properties));
            var methodStatments =
                type.StatementList.Where(s => s.GetType().Name == "CreateMethod").ToList();
            methodStatments.ForEach(ms => content.AppendLine(GenerateMethodSignature((CreateMethod)ms)));
            wrapper = wrapper.Replace("##content##", content.ToString());
            return wrapper;
        }

        public string GenerateProperties(IList<Property> properties)
        {
            var stringBuilder = new StringBuilder();
            var count = properties.Count;
            for (var i = 0; i < count; i++)
            {
                var property = properties[i];
                var propertyText = "";
                propertyText = PropertyText.Replace("##accesslevel##", Access.ToString());
                propertyText = propertyText.Replace("##propertyname##", property.Name);
                if (string.IsNullOrEmpty(property.DefaultValue))
                {
                    propertyText = propertyText.Replace("##typename##", "string");
                }
                else if (RegexUtility.IsString(property.DefaultValue))
                {
                    if (property.DefaultValue == "true" || property.DefaultValue == "false")
                    {
                        propertyText = propertyText.Replace("##typename##", "bool");
                        if (property.DefaultValue == "true")
                        {
                            propertyText = OverrideDefault(propertyText, property.DefaultValue, property.Name, "bool");
                        }
                    }
                    else
                    {
                        propertyText = propertyText.Replace("##typename##", "string");
                        propertyText = OverrideDefault(propertyText, "\"" + property.DefaultValue + "\"", property.Name, "string");
                    }
                }
                else if (RegexUtility.IsInteger(property.DefaultValue))
                {
                    propertyText = propertyText.Replace("##typename##", "int");
                    if (property.DefaultValue != "0")
                    {
                        propertyText = OverrideDefault(propertyText, property.DefaultValue, property.Name, "int");
                    }
                }
                else if (RegexUtility.IsDecimal(property.DefaultValue))
                {
                    propertyText = propertyText.Replace("##typename##", "decimal");
                    if (property.DefaultValue != "0.0")
                    {
                        propertyText = OverrideDefault(propertyText, property.DefaultValue, property.Name, "decimal");
                    }
                }
                stringBuilder.Append(propertyText);
            }
            return stringBuilder.ToString();
        }

        public string GenerateMethodSignature(CreateMethod method)
        {
            var methodText = MethodText.Replace("##accesslevel##", Access.ToString());
            var _params = new StringBuilder();
            var signature = methodText.Replace("##methodname##", method.TargetMethod.Name);
            //TODO: Add support for methods with a return type - is this needed?
            signature = signature.Replace("##returntype##", "void");
            var paramCount = method.TargetMethod.Objects.Count;
            for (var j = 1; j < paramCount; j++)
            {
                var parameter = method.TargetMethod.Objects[j];
                var instanceName = "";
                if (!string.IsNullOrEmpty(parameter.Instance))
                {
                    instanceName = parameter.Instance;
                }
                else
                {
                    instanceName = parameter.Name.ToLower() + InstanceIdentifier;
                    InstanceIdentifier++;
                }
                var delimiter = j < (paramCount - 1) ? ", " : string.Empty;
                _params.Append(string.Format("{0} {1}{2}", parameter.Name, instanceName, delimiter));
            }
            signature = signature.Replace("##params##", _params.ToString());
            return signature;
        }

        public string GenerateAsserts(Object _object, IList<Constraint> constraints)
        {
            var text = new StringBuilder();
            var count = constraints.Count;
            for (var i = 0; i < count; i++)
            {
                var constraint = constraints[i];
                var property = constraint.Property;
                text.AppendLine(AssertText.Replace("##clause##", string.Format("{0}.{1} {2} {3}", _object.Instance, property.Name, property.Operators[0].Value, property.Value)));
            }
            return text.ToString();
        }

        public string OverrideDefault(string text, string value, string propertyName, string type)
        {
            //text = text.Insert(0, string.Format("\t\t\tprivate {0} _{1} = {2};\n", type, propertyName, value));
            //text = text.Replace("{ get; set; }", string.Format("{{ get {{ return _{0}; }} set {{ _{0} = value; }}", propertyName));
            return text;
        }

        #region TextTemplates

        public readonly string TestFixtureText = "#region Using Statements\nusing NUnit.Framework;\n#endregion\n\nnamespace <<ProjectName>>.bdUnit.Interfaces \n{##interfaces##\n}\n\nnamespace <<ProjectName>>.bdUnit.Tests \n{\n\t[TestFixture]\n\tpublic class ##fixturename##\n\t{\n##tests##\t}\n}";

        public readonly string TestText = "\n\t\t[Test]\n\t\tpublic void ##testname##()";

        public readonly string MethodText = "\t\t##accesslevel## virtual ##returntype## ##methodname##(##params##) {}";

        public readonly string PropertyText = "\t\t##accesslevel## ##typename## ##propertyname## { get; set; }\n";

        public readonly string TypeText = "\n\n\tpublic interface I##typename##\n\t{\n##content##\t}";

        public readonly string AssertText = "\t\t\tAssert.IsTrue(##clause##);";

        #endregion
    }
}