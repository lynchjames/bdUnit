#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class Count
    {
        public Count()
        {
            Operators = new List<Operator>();
        }

        public string Value { get; set; }
        public List<Operator> Operators { get; set; }
    }
}