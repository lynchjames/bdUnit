using System.Collections.Generic;
using Core.Enum;

namespace bdUnit.Core.AST
{
    public interface IProperty
    {
        string Name { get; set; }
        string Value { get; set; }
        DefaultValue DefaultValue { get; set; }
        IList<Operator> Operators { get; set; }
        string Relation { get; set; }
        RelationQualifiedEnum GetRelationQualifiedEnum();
    }
}
