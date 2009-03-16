#region Using Statements



#endregion

#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class When : IStatement
    {
        public When()
        {
            Loop = new Loop();
            TargetList = new List<Target>();
            Constraints = new List<Constraint>();
        }

        public Loop Loop { get; set; }
        public List<Target> TargetList { get; set; }
        public List<Constraint> Constraints { get; set; }
    }
}