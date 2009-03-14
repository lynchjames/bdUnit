#region Using Statements



#endregion

using System.Collections.Generic;

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
        public IList<Target> TargetList { get; set; }
        public IList<Constraint> Constraints { get; set; }
    }
}