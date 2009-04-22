#region Using Statements

using System.Collections.Generic;
using bdUnit.Core.Enum;

#endregion

namespace bdUnit.Core.AST
{
    public interface IProperty
    {
        string Name { get; set; }
        string Value { get; set; }
        DefaultValue DefaultValue { get; set; }
        List<Operator> Operators { get; set; }
        string Relation { get; set; }
        RelationQualifiedEnum GetRelationQualifiedEnum();
    }
}