#region Using Statements



#endregion

namespace bdUnit.Core.AST
{
    public class When : IStatement
    {
        public When()
        {
            Loop = new Loop();
            TargetMethod = new TargetMethod();
        }

        public Loop Loop { get; set; }

        #region IStatement Members

        public TargetMethod TargetMethod { get; set; }

        #endregion
    }
}