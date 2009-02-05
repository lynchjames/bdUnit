#region Using Statements

using System.Collections.Generic;
using System.Diagnostics;

#endregion

namespace bdUnit.Core.AST
{
    public class Loop : IStatement
    {
        public Loop()
        {
            Constraints = new List<Constraint>();
            Objects = new List<Object>();
        }

        public IList<Object> Objects { get; set; }
        public IList<Constraint> Constraints { get; set; }

        #region IStatement Members

        public TargetMethod TargetMethod { get; set; }

        #endregion
    }
}