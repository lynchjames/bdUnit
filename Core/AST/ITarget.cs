#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public interface ITarget
    {
        IList<Constraint> Constraints { get; set; }
        string Name { get; set; }
        IList<Object> Objects { get; set; }
    }
}
