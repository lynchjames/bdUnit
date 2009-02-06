#region Using Statements

using System;
using System.Collections.Generic;
using Core.Enum;

#endregion

namespace bdUnit.Core.AST
{
    public class Property
    {
        public Property()
        {
            Object = new Object();
            Operators = new List<Operator>();
            DefaultValue = new DefaultValue();
        }

        public string Name { get; set; }
        public string Value { get; set; }
        public DefaultValue DefaultValue { get; set; }
        public Object Object { get; set; }
        public List<Operator> Operators { get; set; }
        public string Relation { get; set; }

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