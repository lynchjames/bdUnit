#region Using Statements

using System.Diagnostics;

#endregion

namespace bdUnit.Core.AST
{
    public class Statement
    {
        public CreateMethod CreateMethod { get; set; }
        public When When { get; set; }
    }
}