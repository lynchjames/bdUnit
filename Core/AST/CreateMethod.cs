#region Using Statements

using System.Diagnostics;

#endregion

namespace bdUnit.Core.AST
{
    public class CreateMethod : IStatement
    {
        #region IStatement Members

        public TargetMethod TargetMethod { get; set; }

        #endregion
    }
}