#region Using Statements

using System.Diagnostics;

#endregion

namespace bdUnit.Core.AST
{
    public class Constraint
    {
        public Constraint()
        {
            Property = new Property();
        }

        public Property Property { get; set; }
    }
}