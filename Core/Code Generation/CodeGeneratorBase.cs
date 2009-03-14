﻿#region Using Statements

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;
using bdUnit.Core.Utility;
using Core.Enum;
using Object=bdUnit.Core.AST.Object;
using Type=bdUnit.Core.AST.Type;

#endregion

namespace bdUnit.Core
{
    public class CodeGeneratorBase : ICodeGenerator
    {
        public CodeGeneratorBase(string fixtureText, string testText, string methodText, string propertyText, string typeText, string assertText)
        {
            TestFixtureText = fixtureText;
            TestText = testText;
            MethodText = methodText;
            PropertyText = propertyText;
            TypeText = typeText;
            AssertText = assertText;
        }

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
            stringBuilder = GenerateMethods(statementList, stringBuilder);
            return stringBuilder.ToString();
        }

        //TODO Need to be able to test the returned object from a method?
        public StringBuilder GenerateMethods(IList<IStatement> statements, StringBuilder stringBuilder)
        {
            var statementCount = statements.Count;
            if (statementCount > 0)
            {
                for (var i = 0; i < statementCount; i++)
                {
                    var statement = statements[i];
                    var whenStatement = statement as When;
                    if (whenStatement == null) continue;
                    if (whenStatement.TargetList.Count > 1)
                    {
                        stringBuilder = GenerateMethodsForTargets(whenStatement.TargetList as List<Target>, stringBuilder);
                    }
                    else
                    {
                        var target = whenStatement.TargetList[0];
                        if (target.TargetProperty != null)
                        {
                            var targetProperty = target.TargetProperty;
                            stringBuilder = GenerateMethodForTargetProperty(targetProperty, stringBuilder);
                        }
                        else
                        {
                            var variables = new StringBuilder();
                            var targetMethod = target.TargetMethod;
                            //TODO Test specific property values on object after method used
                            stringBuilder = GenerateMethodForTargetMethod(targetMethod, variables, whenStatement, stringBuilder);
                        }
                    }
                    if (whenStatement.Constraints.Count > 0)
                    {
                        for (var k = 0; k < whenStatement.Constraints.Count; k++)
                        {
                            var constraint = whenStatement.Constraints[k];
                            if (constraint.Objects.Count > 0)
                            {
                                stringBuilder.Append(GenerateAsserts(constraint.Objects[0],
                                                                     new List<Constraint> { constraint }));
                            }
                            else if (constraint.Property != null)
                            {
                                stringBuilder.Append(GenerateAsserts(constraint.Property.Object,
                                                                     new List<Constraint> { constraint }));
                            }
                        }
                    }
                    //TODO Loops are broken
                    //if (whenStatement.Loop != null)
                    //{
                    //    var loop = whenStatement.Loop;
                    //    stringBuilder.Append(GenerateAsserts(loop.TargetMethod.Objects[0], loop.Constraints));
                    //    var reciprocalRelationships =
                    //        loop.Constraints.Where(
                    //            con =>
                    //            con.Property.GetRelationQualifiedEnum() == RelationQualifiedEnum.Reciprocal).ToList();
                    //    if (reciprocalRelationships.Count > 0)
                    //    {
                    //        reciprocalRelationships.ForEach(
                    //            r =>
                    //            {
                    //                var reciprocalAssert = CodeUtility.Parameterize(RelationQualifiedEnum.Reciprocal,
                    //                                                                new List<Property> { r.Property },
                    //                                                                AssertText, loop.TargetMethod.Objects);
                    //                WriteToTrace(stringBuilder, reciprocalAssert);
                    //                stringBuilder.Append(reciprocalAssert);
                    //            });
                    //    }
                    //}
                    stringBuilder.AppendLine("\t\t}");
                }
            }
            return stringBuilder;
        }

        private StringBuilder GenerateMethodsForTargets(List<Target> list, StringBuilder stringBuilder)
        {
            var titleSet = false;
            var previouslyCreated = new List<string>();
            list.ForEach(x =>
                             {
                                 if (x.TargetProperty != null)
                                 {
                                     var property = x.TargetProperty;
                                     var obj = property.Objects[0];
                                     if (!titleSet)
                                     {
                                        var title = string.Format("When_{0}_Is_Set_...", property.Name);
                                        stringBuilder.AppendLine(TestText.Replace("##testname##", title));
                                        stringBuilder.AppendLine("\t\t{");
                                        titleSet = true;
                                     }
                                     if (!previouslyCreated.Contains(obj.Instance.Value))
                                     {
                                         stringBuilder.AppendLine(
                                             string.Format(
                                                 "\t\t\tI{1} {0} = ObjectFactory.GetNamedInstance<I{1}>(\"bdUnit\");",
                                                 obj.Instance.Value, obj.Name));
                                         previouslyCreated.Add(obj.Instance.Value);
                                     }
                                     stringBuilder.AppendLine(string.Format("\t\t\t{0}.{1} {2} {3};", obj.Instance.Value, property.Name, property.Operators[0].Value.Replace("==", "="), property.Value));
                                 }
                                 else
                                 {
                                     var target = x.TargetMethod;
                                     var objects = target.Objects;
                                     var obj = objects[0];
                                     var otherObj = objects[1];
                                     var variables = new StringBuilder();
                                     if (!previouslyCreated.Contains(obj.Instance.Value))
                                     {
                                         variables.Append(string.Format("\t\t\tI{1} {0} = ObjectFactory.GetNamedInstance<I{1}>(\"bdUnit\");\n",
                                                                    obj.Instance.Value, obj.Name));
                                         previouslyCreated.Add(obj.Instance.Value);
                                     }
                                     if (!previouslyCreated.Contains(otherObj.Instance.Value))
                                     {
                                         variables.Append(string.Format("\t\t\tI{1} {0} = ObjectFactory.GetNamedInstance<I{1}>(\"bdUnit\");\n",
                                                                    otherObj.Instance.Value, otherObj.Name));
                                         previouslyCreated.Add(otherObj.Instance.Value);
                                     }
                                     var methodUsage = string.Format("\t\t\t{0}.{1}({2});\n", obj.Instance.Value, target.Name,
                                                                     otherObj.Instance.Value);

                                     if (!titleSet)
                                     {
                                         var title = string.Format("When_{0}_{1}_{2}", obj.Name, target.Name,
                                                                   otherObj.Name);
                                         stringBuilder.AppendLine(TestText.Replace("##testname##", title));
                                         stringBuilder.AppendLine("\t\t{");
                                         titleSet = true;
                                     }
                                     stringBuilder.Append(variables).Append(methodUsage);
                                 }
                             });
            return stringBuilder;
        }

        private StringBuilder GenerateMethodForTargetProperty(TargetProperty property, StringBuilder stringBuilder)
        {
            var obj = property.Objects[0];
            var title = string.Format("When_{0}_{1}_Is_Set", obj.Name, property.Name);
            stringBuilder.AppendLine(TestText.Replace("##testname##", title));
            stringBuilder.AppendLine("\t\t{");
            stringBuilder.AppendLine(string.Format("\t\t\tI{1} {0} = ObjectFactory.GetNamedInstance<I{1}>(\"bdUnit\");",
                                           obj.Instance.Value, obj.Name));
            stringBuilder.AppendLine(string.Format("\t\t\t{0}.{1} {2} {3};", obj.Instance.Value, property.Name, property.Operators[0].Value.Replace("==", "="), property.Value));
            //stringBuilder.Append(GenerateAsserts(property));
            return stringBuilder;
        }

        private StringBuilder GenerateMethodForTargetMethod(TargetMethod target, StringBuilder variables, When whenStatement, StringBuilder stringBuilder)
        {
            var objects = target.Objects;
            var obj = objects[0];
            var otherObj = objects[1];
            variables.Append(string.Format("\t\t\tI{1} {0} = ObjectFactory.GetNamedInstance<I{1}>(\"bdUnit\");\n",
                                           obj.Instance.Value, obj.Name));
            variables.Append(string.Format("\t\t\tI{1} {0} = ObjectFactory.GetNamedInstance<I{1}>(\"bdUnit\");\n",
                                           otherObj.Instance.Value, otherObj.Name));
            var methodUsage = string.Format("\t\t\t{0}.{1}({2});\n", obj.Instance.Value, target.Name,
                                            otherObj.Instance.Value);

            //TODO: Add logic to determine type constuctor @User(Name = Jim, Age = 25) should correspond to var Jim = new User() {Name = "Jim", Age = 25};
            var title = string.Format("When_{0}_{1}_{2}", obj.Name, target.Name, otherObj.Name);
            stringBuilder.AppendLine(TestText.Replace("##testname##", title));
            stringBuilder.AppendLine("\t\t{");
            stringBuilder.Append(variables).Append(methodUsage);
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
                if (!string.IsNullOrEmpty(property.Relation) && property.GetRelationQualifiedEnum() != RelationQualifiedEnum.None && property.DefaultValue != null && property.DefaultValue.Object != null)
                {
                    propertyText = CodeUtility.Parameterize(property.GetRelationQualifiedEnum(), new List<Property> { property },
                                             propertyText, null);

                }
                else if (string.IsNullOrEmpty(property.DefaultValue.Value))
                {
                    if (property.DefaultValue.Object.Name != null)
                    {
                        propertyText = CodeUtility.Parameterize(RelationQualifiedEnum.OneToOne, new List<Property> {property}, propertyText, null);
                    }
                    propertyText = propertyText.Replace("##typename##", "string");
                }
                else if (RegexUtility.IsDateTime(property.DefaultValue.Value))
                {
                    propertyText = propertyText.Replace("##typename##", "DateTime");
                }
                else if (RegexUtility.IsString(property.DefaultValue.Value))
                {
                    if (property.DefaultValue.Value == "true" || property.DefaultValue.Value == "false")
                    {
                        propertyText = propertyText.Replace("##typename##", "bool");
                        if (property.DefaultValue.Value == "true")
                        {
                            propertyText = OverrideDefault(propertyText, property.DefaultValue.Value, property.Name, "bool");
                        }
                    }
                    else
                    {
                        propertyText = propertyText.Replace("##typename##", "string");
                        propertyText = OverrideDefault(propertyText, "\"" + property.DefaultValue.Value + "\"", property.Name, "string");
                    }
                }
                else if (RegexUtility.IsDecimal(property.DefaultValue.Value))
                {
                    propertyText = propertyText.Replace("##typename##", "decimal");
                    if (property.DefaultValue.Value != "0.0")
                    {
                        propertyText = OverrideDefault(propertyText, property.DefaultValue.Value, property.Name, "decimal");
                    }
                }
                else if (RegexUtility.IsInteger(property.DefaultValue.Value))
                {
                    propertyText = propertyText.Replace("##typename##", "int");
                    if (property.DefaultValue.Value != "0")
                    {
                        propertyText = OverrideDefault(propertyText, property.DefaultValue.Value, property.Name, "int");
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
            signature = signature.Replace("##returntype##", "void");
            var paramCount = method.TargetMethod.Objects.Count;
            for (var j = 1; j < paramCount; j++)
            {
                var parameter = method.TargetMethod.Objects[j];
                var instanceName = "";
                if (!string.IsNullOrEmpty(parameter.Instance.Value))
                {
                    instanceName = parameter.Instance.Value;
                }
                else
                {
                    instanceName = parameter.Name.ToLower();
                }
                var delimiter = j < (paramCount - 1) ? ", " : string.Empty;
                _params.Append(string.Format("I{0} {1}{2}", parameter.Name, instanceName, delimiter));
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
                if (string.IsNullOrEmpty(constraint.Property.Relation))
                {
                    if (RegexUtility.IsBool(property.Value))
                    {
                        var value = Boolean.Parse(property.Value);
                        var boolQualifier = value ? string.Empty : "!";
                        var boolStatement = AssertText.Replace("##clause##",
                                                               string.Format("{0}{1}.{2}", boolQualifier,
                                                                             _object.Instance.Value, property.Name));
                        WriteToTrace(text, boolStatement);
                        text.AppendLine(boolStatement);
                    }
                    else if (RegexUtility.IsDateTime(property.Value))
                    {
                        var dtInstance = "dateTime" + InstanceIdentifier;
                        var dateTimeStatement = string.Format("\t\t\tvar {0} = DateTime.Parse(\"{1}\");", dtInstance,
                                                              property.Value);
                        WriteToTrace(text, dateTimeStatement);
                        text.AppendLine(dateTimeStatement);
                        var dateTimeAssert = AssertText.Replace("##clause##",
                                                                string.Format("{0}.{1} {2} {3}", _object.Instance.Value,
                                                                              property.Name, property.Operators[0].Value,
                                                                              dtInstance));
                        WriteToTrace(text, dateTimeAssert);
                        text.AppendLine(dateTimeAssert);
                        InstanceIdentifier++;
                    }
                    else if (property.Operators[0].Value.Contains("contains"))
                    {
                        var boolQualifier = property.Operators[0].Value == "contains" ? "" : "!";
                        var containsAssert = AssertText.Replace("##clause##",
                                                                string.Format("{0}{1}.{2}.Contains({3})", boolQualifier,
                                                                              _object.Instance.Value, property.Name,
                                                                              property.Value));
                        WriteToTrace(text, containsAssert);
                        text.AppendLine(containsAssert);
                    }
                    else
                    {
                        var valueAssert = AssertText.Replace("##clause##",
                                                             string.Format("{0}.{1} {2} {3}", _object.Instance.Value,
                                                                           property.Name, property.Operators[0].Value,
                                                                           property.Value));
                        WriteToTrace(text, valueAssert);
                        text.AppendLine(valueAssert);
                    }
                }
            }
            return text.ToString();
        }

        //public string GenerateAsserts(TargetProperty property)
        //{
        //    var text = new StringBuilder();
        //    var count = property.Constraints.Count;
        //    for (var i = 0; i < count; i++)
        //    {
        //        var constraint = property.Constraints[i];
        //        var constrainedProperty = constraint.Property;
        //        var instance = property.Objects[0].Instance.Value;
        //        if (RegexUtility.IsBool(constrainedProperty.Value))
        //        {
        //            var value = Boolean.Parse(constrainedProperty.Value);
        //            var boolQualifier = value ? string.Empty : "!";
        //            var boolAssert = AssertText.Replace("##clause##",
        //                                                string.Format("{0}{1}.{2}", boolQualifier, instance,
        //                                                              constrainedProperty.Name));
        //            WriteToTrace(text, boolAssert);
        //            text.AppendLine();
        //        }
        //        else if (constrainedProperty.Operators[0].Value.Contains("contains"))
        //        {
        //            var boolQualifier = property.Operators[0].Value == "contains" ? "" : "!";
        //            var containsAssert = AssertText.Replace("##clause##",
        //                                                    string.Format("{0}{1}.{2}.Contains({3})", boolQualifier,
        //                                                                  instance, constrainedProperty.Name,
        //                                                                  constrainedProperty.Value));
        //            WriteToTrace(text, containsAssert);
        //            text.AppendLine(containsAssert);
        //        }
        //        else if (RegexUtility.IsDateTime(constrainedProperty.Value))
        //        {
        //            var dtInstance = "dateTime" + InstanceIdentifier;
        //            var dateTimeStatment = string.Format("\t\t\tvar {0} = DateTime.Parse(\"{1}\");", dtInstance,
        //                                                 constrainedProperty.Value);
        //            WriteToTrace(text, dateTimeStatment);
        //            text.AppendLine(dateTimeStatment);
        //            var dateTimeAssert = AssertText.Replace("##clause##",
        //                                                    string.Format("{0}.{1} {2} {3}", instance,
        //                                                                  constrainedProperty.Name,
        //                                                                  constrainedProperty.Operators[0].Value,
        //                                                                  dtInstance));
        //            WriteToTrace(text, dateTimeAssert);
        //            text.AppendLine(dateTimeAssert);
        //            InstanceIdentifier++;
        //        }
        //        else
        //        {
        //            var valueAssert = AssertText.Replace("##clause##",
        //                                                 string.Format("{0}.{1} {2} {3}", instance,
        //                                                               constrainedProperty.Name,
        //                                                               property.Operators[0].Value,
        //                                                               constrainedProperty.Value));
        //            WriteToTrace(text, valueAssert);
        //            text.AppendLine(valueAssert);
        //        }
        //    }
        //    return text.ToString();
        //}

        public string OverrideDefault(string text, string value, string propertyName, string type)
        {
            //text = text.Insert(0, string.Format("\t\t\tprivate {0} _{1} = {2};\n", type, propertyName, value));
            //text = text.Replace("{ get; set; }", string.Format("{{ get {{ return _{0}; }} set {{ _{0} = value; }}", propertyName));
            return text;
        }

        private static void WriteToTrace(StringBuilder text, string statement)
        {
            statement = statement.Replace("\t", string.Empty).Replace("\n", string.Empty).Replace("\r", string.Empty).Replace("\"", @"\" + "\"");
            text.AppendLine(string.Format("\t\t\tDebug.WriteLine(\"{0}\");", statement));
            return;
        }

        #region TextTemplates

        public readonly string TestFixtureText;

        public readonly string TestText;

        public readonly string MethodText;

        public readonly string PropertyText;

        public readonly string TypeText;

        public readonly string AssertText;

        #endregion
    }
}
