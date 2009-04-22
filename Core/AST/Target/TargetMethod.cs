#region Using Statements

using System;
using System.Collections.Generic;
using bdUnit.Core.Enum;

#endregion

namespace bdUnit.Core.AST
{
    public class TargetMethod : ITarget
    {
        public TargetMethod()
        {
            ConcreteClasses = new List<ConcreteClass>();
            Properties = new List<Property>();
        }

        public List<Property> Properties { get; set; }
        public Loop Loop { get; set; }
        public string Relation { get; set; }

        #region ITarget Members

        public string Name { get; set; }
        public List<ConcreteClass> ConcreteClasses { get; set; }

        #endregion

        public RelationQualifiedEnum GetRelationQualifiedEnum()
        {
            try
            {
                return (RelationQualifiedEnum) System.Enum.Parse(typeof (RelationQualifiedEnum), Relation);
            }
            catch (Exception)
            {
                return RelationQualifiedEnum.None;
            }
        }
    }
}