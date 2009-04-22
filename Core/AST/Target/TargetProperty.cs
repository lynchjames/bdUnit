#region Using Statements

using System;
using System.Collections.Generic;
using bdUnit.Core.Enum;

#endregion

namespace bdUnit.Core.AST
{
    public class TargetProperty : IProperty, ITarget
    {
        public TargetProperty()
        {
            ConcreteClasses = new List<ConcreteClass>();
            Operators = new List<Operator>();
            DefaultValue = new DefaultValue();
        }

        #region IProperty Members

        public string Name { get; set; }
        public string Value { get; set; }
        public DefaultValue DefaultValue { get; set; }
        public List<Operator> Operators { get; set; }
        public string Relation { get; set; }

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

        #endregion

        #region ITarget Members

        public List<ConcreteClass> ConcreteClasses { get; set; }

        #endregion
    }
}