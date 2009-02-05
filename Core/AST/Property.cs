#region Using Statements

using System.Collections.Generic;
using System.Diagnostics;
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
        }

        public string Name { get; set; }
        public string Value { get; set; }
        public string DefaultValue { get; set; }
        public Object Object { get; set; }
        public List<Operator> Operators { get; set; }
        public string Relation { get; set; }
        public RelationEnum _Relation { get { return (RelationEnum)System.Enum.Parse(typeof(RelationEnum), Relation); } }

        public void Print()
        {
            Debug.WriteLine("\t\t\tName: " + Name);
            Debug.WriteLine("\t\t\tValue: " + Value);
            Debug.WriteLine("\t\t\tObject: " + Object.Name);
            Debug.WriteLine("\t\t\tOperator: " + Operators);
        }
    }
}