#region Using Statements

using System;
using System.Collections.Generic;
using Core.Enum;

#endregion

namespace bdUnit.Core.AST
{
    public class TargetProperty : IProperty, ITarget
    {
        public TargetProperty()
        {
            Objects = new List<Object>();
            Operators = new List<Operator>();
            DefaultValue = new DefaultValue();
            Constraints = new List<Constraint>();
        }

        public string Name { get; set; }
        public string Value { get; set; }
        public DefaultValue DefaultValue { get; set; }
        public IList<Object> Objects { get; set; }
        public IList<Operator> Operators { get; set; }
        public string Relation { get; set; }
        public IList<Constraint> Constraints { get; set; }

        public RelationQualifiedEnum GetRelationQualifiedEnum()
        {
            try
            {
                return (RelationQualifiedEnum)System.Enum.Parse(typeof(RelationQualifiedEnum), Relation);
            }
            catch (Exception)
            {
                return RelationQualifiedEnum.None;
            }
        }
    }
}
