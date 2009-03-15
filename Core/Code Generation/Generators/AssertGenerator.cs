using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Utility;
using Core.Enum;
using Object=bdUnit.Core.AST.Object;

namespace bdUnit.Core.Generators
{
    public interface IAssertGenerator
    {
        string Generate(Object _object, IList<Constraint> constraints);
        StringBuilder GenerateForLoop(When whenStatement, StringBuilder stringBuilder);
    }

    public class AssertGenerator : GeneratorBase, IAssertGenerator
    {
        public int InstanceIdentifier = 0;

        public AssertGenerator(string assertText)
        {
            AssertText = assertText;
        }

        public string Generate(Object _object, IList<Constraint> constraints)
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

        public StringBuilder GenerateForLoop(When whenStatement, StringBuilder stringBuilder)
        {
            if (whenStatement.Loop != null && whenStatement.Loop.Constraints.Count > 0)
            {
                var loop = whenStatement.Loop;
                var instanceObjects = ASTUtility.FindInstantiatedObjects(whenStatement);
                instanceObjects.ForEach(io => stringBuilder.Append(Generate(io, loop.Constraints)));
                var reciprocalRelationships =
                    loop.Constraints.Where(
                        con =>
                        con.Property.GetRelationQualifiedEnum() == RelationQualifiedEnum.Reciprocal).ToList();
                if (reciprocalRelationships.Count > 0)
                {
                    reciprocalRelationships.ForEach(
                        r =>
                        {
                            var target =
                                whenStatement.TargetList.Where(
                                    x => x.TargetMethod != null && x.TargetMethod.Objects.Count == 2).FirstOrDefault();
                            var reciprocalAssert = CodeUtility.Parameterize(RelationQualifiedEnum.Reciprocal,
                                                                            new List<Property> { r.Property },
                                                                            AssertText, target.TargetMethod.Objects);
                            WriteToTrace(stringBuilder, reciprocalAssert);
                            stringBuilder.Append(reciprocalAssert);
                        });
                }
            }
            return stringBuilder;
        }
    }
}