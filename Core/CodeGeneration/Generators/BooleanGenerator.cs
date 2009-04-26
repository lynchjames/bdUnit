#region Using Statements

using System;
using System.Collections.Generic;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Extensions;
using bdUnit.Core.Templates;
using bdUnit.Core.Utility;

#endregion

namespace bdUnit.Core.Generators
{
    public class BooleanGenerator
    {
        private static int InstanceIdentifier = 20;

        public static string Generate(List<Target> targets)
        {
            var text = new StringBuilder();
            var count = targets.Count;
            for (var i = 0; i < count; i++)
            {
                var target = targets[i];
                var _concreteClass = target.TargetProperty.ConcreteClasses[0];
                var property = target.TargetProperty;
                if (string.IsNullOrEmpty(property.Relation))
                {
                    var boolStatement = string.Empty;
                    if (property.Count != null && property.Value == null)
                    {
                        var countValue = Int32.Parse(property.Count.Value);
                        var countOperator = property.Count.Operators.Count > 0
                                                   ? property.Count.Operators[0].Value
                                                   : "==";
                        boolStatement = string.Format("{0}.{1}.Count {2} {3}",
                                               _concreteClass.Instance.Value, property.Name, countOperator, countValue);
                    }
                    else if (RegexUtility.IsBool(property.Value))
                    {
                        var value = Boolean.Parse(property.Value);
                        var boolQualifier = value ? string.Empty : "!";
                        boolStatement = string.Format("{0}{1}.{2}", boolQualifier, _concreteClass.Instance.Value, property.Name);
                    }
                    else if (RegexUtility.IsDateTime(property.Value))
                    {
                        var dtInstance = "dateTime" + InstanceIdentifier;
                        var dateTimeStatement =
                            new Dictionary<string, object> { { "instance", dtInstance }, { "value", property.Value } }.
                                AsNVelocityTemplate(TemplateEnum.DateTimeVariable);
                        text.AppendLine(dateTimeStatement);
                        boolStatement = string.Format("{0}.{1} {2} {3}", _concreteClass.Instance.Value,
                                               property.Name, property.Operators[0].Value,
                                               dtInstance);
                        InstanceIdentifier++;
                    }
                    else if (property.Operators[0].Value.Contains("contains"))
                    {
                        var boolQualifier = property.Operators[0].Value == "contains" ? "" : "!";
                        boolStatement = string.Format("{0}{1}.{2}.Contains({3})", boolQualifier,
                                               _concreteClass.Instance.Value, property.Name,
                                               property.Value);
                    }
                    else
                    {
                        boolStatement = string.Format("{0}.{1} {2} {3}", _concreteClass.Instance.Value,
                                               property.Name, property.Operators[0].Value,
                                               property.Value);
                    }
                    text.Append(" && " + boolStatement);
                }
            }
            return text.ToString();
        }
    }
}