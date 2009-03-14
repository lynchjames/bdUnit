#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public interface ITarget
    {
        string Name { get; set; }
        IList<Object> Objects { get; set; }
    }
}
