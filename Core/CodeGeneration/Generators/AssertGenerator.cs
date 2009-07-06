#region Using Statements

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;
using bdUnit.Core.Extensions;
using bdUnit.Core.Templates;
using bdUnit.Core.Utility;

#endregion

namespace bdUnit.Core.Generators
{
    public interface IAssertGenerator
    {
        string Generate(ConcreteClass _concreteClass, List<Constraint> constraints);
        StringBuilder GenerateForLoop(When whenStatement, StringBuilder stringBuilder);
    }

    public class AssertGenerator : GeneratorBase, IAssertGenerator
    {
        public int InstanceIdentifier;

        public AssertGenerator(string assertText)
        {
            AssertText = assertText;
        }

        #region IAssertGenerator Members

        public string Generate(ConcreteClass _concreteClass, List<Constraint> constraints)
        {
            var text = new StringBuilder();
            var count = constraints.Count;
            for (var i = 0; i < count; i++)
            {
                var constraint = constraints[i];
                var property = constraint.Property;
                  if (constraint.ConcreteClassPropertyMapping != null)
                {
                    var classes = constraint.ConcreteClassPropertyMapping.ConcreteClasses;
                    var properties = constraint.ConcreteClassPropertyMapping.Properties;
                    var @operator = constraint.Operators[0].Value;
                    var assert = string.Empty;
                    if (@operator.Contains("contains"))
                    {
                        var boolQualifier = @operator.ToLower() == "contains" ? "" : "!";
                        assert = string.Format("{0}{1}.{2}.Contains({3})", boolQualifier,
                                               classes[0].Instance.Value, properties[0].Name,
                                               classes[1].Instance.Value);
                    }
                    else
                    {
                        assert = string.Format("{0}.{1} {2} {3}.{4}", classes[0].Instance.Value, properties[0].Name, @operator, classes[1].Instance.Value, properties[1].Name);   
                    }
                    text.AppendLine(AssertText.Replace("##clause##", WriteAssertMessage(assert)));
                }
                else
                {
                    GenerateSingleAssert(property, _concreteClass, text);
                }
            }
            return text.ToString();
        }

        private string GetContainsAssert(string @operator, ConcreteClass _concreteClass, Property property)
        {
            string assert;
            var boolQualifier = @operator.ToLower() == "contains" ? "" : "!";
            assert = string.Format("{0}{1}.{2}.Contains({3})", boolQualifier,
                                   _concreteClass.Instance.Value, property.Name,
                                   property.Value);
            return assert;
        }

        private void GenerateSingleAssert(Property property, ConcreteClass _concreteClass, StringBuilder text)
        {
            if (string.IsNullOrEmpty(property.Relation))
            {
                var assert = string.Empty;
                var assertBody = string.Empty;
                if (property.Count != null && property.Value == null)
                {
                    var countValue = Int32.Parse(property.Count.Value);
                    var countOperator = property.Count.Operators.Count > 0
                                            ? property.Count.Operators[0].Value
                                            : "==";
                    assert = string.Format("{0}.{1}.Count {2} {3}",
                                           _concreteClass.Instance.Value, property.Name, countOperator, countValue);
                    assertBody = AssertText.Replace("##clause##", WriteAssertMessage(assert));
                }
                else if (RegexUtility.IsBool(property.Value))
                {
                    var value = Boolean.Parse(property.Value);
                    var boolQualifier = value ? string.Empty : "!";
                    assert = string.Format("{0}{1}.{2}", boolQualifier, _concreteClass.Instance.Value, property.Name);
                    assertBody = AssertText.Replace("##clause##", WriteAssertMessage(assert));
                }
                else if (RegexUtility.IsDateTime(property.Value))
                {
                    var dtInstance = "dateTime" + InstanceIdentifier;
                    var dateTimeStatement =
                        new Dictionary<string, object> {{"instance", dtInstance}, {"value", property.Value}}.
                            AsNVelocityTemplate(TemplateEnum.DateTimeVariable);
                    text.AppendLine(dateTimeStatement);
                    assert = string.Format("{0}.{1} {2} {3}", _concreteClass.Instance.Value,
                                           property.Name, property.Operators[0].Value,
                                           dtInstance);
                    assertBody = AssertText.Replace("##clause##", WriteAssertMessage(assert));
                    InstanceIdentifier++;
                }
                else if (property.Operators[0].Value.Contains("contains"))
                {
                    assertBody = AssertText.Replace("##clause##", WriteAssertMessage(GetContainsAssert(property.Operators[0].Value, _concreteClass, property)));
                }
                else
                {
                    assert = string.Format("{0}.{1} {2} {3}", _concreteClass.Instance.Value,
                                           property.Name, property.Operators[0].Value,
                                           property.Value);
                    assertBody = AssertText.Replace("##clause##", WriteAssertMessage(assert));
                }
                text.AppendLine(assertBody);
            }
        }

        public StringBuilder GenerateForLoop(When whenStatement, StringBuilder stringBuilder)
        {
            if (whenStatement.Loop != null && whenStatement.Loop.Constraints.Count > 0)
            {
                var loop = whenStatement.Loop;
                var instanceObjects = ASTUtility.FindInstantiatedConcreteClasses(whenStatement);
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
                                        x => x.TargetMethod != null && x.TargetMethod.ConcreteClasses.Count == 2).
                                        FirstOrDefault();
                                var reciprocalAssert = CodeUtility.Parameterize(RelationQualifiedEnum.Reciprocal,
                                                                                   new List<Property> {r.Property},
                                                                                   AssertText,
                                                                                   target.TargetMethod.ConcreteClasses);
                                stringBuilder.Append(reciprocalAssert);
                            });
                }
            }
            return stringBuilder;
        }

        #endregion
    }
}