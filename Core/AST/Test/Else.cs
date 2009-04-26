#region Using Statements

#endregion

#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class Else : IStatement
    {
        public Else()
        {
            Constraints = new List<Constraint>();
        }

        public If If { get; set; }
        public List<Constraint> Constraints { get; set; }
    }
}