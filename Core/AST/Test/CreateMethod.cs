#region Using Statements

#endregion

namespace bdUnit.Core.AST
{
    public class CreateMethod : IStatement
    {
        public TargetMethod TargetMethod { get; set; }
    }
}