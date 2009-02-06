﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using bdUnit.Core.AST;
using Core.Enum;
using Object=bdUnit.Core.AST.Object;

namespace bdUnit.Core.Utility
{
    public class CodeUtility
    {
        public static string Parameterize(RelationQualifiedEnum relation, List<Property> properties, string input, IList<Object> objects)
        {
            var output = new StringBuilder();
            switch (relation)
                    {
                        case RelationQualifiedEnum.OneToOne:
                            output.Append(input.Replace("##typename##",
                                                        string.Format("I{0}",
                                                        properties.ElementAt(0).DefaultValue.Object.Name)));
                            break;

                        case RelationQualifiedEnum.OneToMany:
                            break;
                    
                        case RelationQualifiedEnum.ManyToOne:
                            output.Append(input.Replace("##typename##",
                                                        string.Format("IList<I{0}>", 
                                                        properties.ElementAt(0).DefaultValue.Object.Name)));
                            break;
                
                        case RelationQualifiedEnum.ManyToMany:
                            break;

                        case RelationQualifiedEnum.Reciprocal:
                            // Only used with 2 objects
                            for (int i = 0; i < 2; i++)
                            {
                                var other = i == 0 ? 1 : 0;
                                var property = properties.ElementAt(0);
                                var value = objects[other].Instance.Value;
                                output.AppendLine(input.Replace("##clause##", 
                                                                string.Format("{0}.{1} {2} {3}", 
                                                                objects[i].Instance.Value, 
                                                                property.Name, 
                                                                property.Operators[0].Value, 
                                                                value)));
                            }
                            break;

                    }
            return output.ToString();
        }
    }
}
