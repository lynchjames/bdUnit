#region Using Statements

#endregion

#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class Then : IStatement
    {
        public Then()
        {
            Constraints = new List<Constraint>();
        }

        public List<Constraint> Constraints { get; set; }
    }
}