#region Using Statements

using System;
using System.Collections.Generic;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;
using bdUnit.Core.Utility;

#endregion

namespace bdUnit.Core.Generators
{
    public interface IPropertyGenerator
    {
        string Generate(List<Property> properties);
    }

    public class PropertyGenerator : GeneratorBase, IPropertyGenerator
    {
        public PropertyGenerator(AccessEnum access, string propertyText)
        {
            Access = access;
            PropertyText = propertyText;
        }

        #region IPropertyGenerator Members

        public string Generate(List<Property> properties)
        {
            var stringBuilder = new StringBuilder();
            var count = properties.Count;
            for (var i = 0; i < count; i++)
            { 
                var property = properties[i];
                var propertyText = "";
                propertyText = PropertyText.Replace("##accesslevel##", Access.ToString());
                propertyText = propertyText.Replace("##propertyname##", property.Name);
                if (!string.IsNullOrEmpty(property.Relation) &&
                    property.GetRelationQualifiedEnum() != RelationQualifiedEnum.None && property.DefaultValue != null &&
                    property.DefaultValue.ConcreteClass != null)
                {
                    propertyText = CodeUtility.Parameterize(property.GetRelationQualifiedEnum(),
                                                            new List<Property> {property},
                                                            propertyText, null);
                }
                else if (string.IsNullOrEmpty(property.DefaultValue.Value))
                {
                    if (property.DefaultValue.ConcreteClass.Name != null)
                    {
                        propertyText = CodeUtility.Parameterize(RelationQualifiedEnum.OneToOne,
                                                                new List<Property> {property}, propertyText, null);
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
                            propertyText = OverrideDefault(propertyText, property.DefaultValue.Value, property.Name,
                                                           "bool");
                        }
                    }
                    else if (property.DefaultValue.Value == "id")
                    {
                        propertyText = propertyText.Replace("##typename##", "Guid");
                    }
                    else
                    {
                        propertyText = propertyText.Replace("##typename##", "string");
                        propertyText = OverrideDefault(propertyText, "\"" + property.DefaultValue.Value + "\"",
                                                       property.Name, "string");
                    }
                }
                else if (RegexUtility.IsDouble(property.DefaultValue.Value))
                {
                    propertyText = propertyText.Replace("##typename##", "double");
                    if (property.DefaultValue.Value != "0.0")
                    {
                        propertyText = OverrideDefault(propertyText, property.DefaultValue.Value, property.Name,
                                                       "double");
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

        #endregion

        //Deprecated as Interfaces are created with Auto-Properties only
        [Obsolete]
        public string OverrideDefault(string text, string value, string propertyName, string type)
        {
            //text = text.Insert(0, string.Format("\t\t\tprivate {0} _{1} = {2};\n", type, propertyName, value));
            //text = text.Replace("{ get; set; }", string.Format("{{ get {{ return _{0}; }} set {{ _{0} = value; }}", propertyName));
            return text;
        }
    }
}