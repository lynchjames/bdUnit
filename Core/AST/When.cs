#region Using Statements



#endregion

namespace bdUnit.Core.AST
{
    public class When : IStatement
    {
        public When()
        {
            Loop = new Loop();
            //TargetMethod = new TargetMethod();
            //TargetProperty = new TargetProperty();
        }

        public Loop Loop { get; set; }
        public TargetProperty TargetProperty { get; set; }

        #region IStatement Members

        public TargetMethod TargetMethod { get; set; }

        #endregion
    }
}