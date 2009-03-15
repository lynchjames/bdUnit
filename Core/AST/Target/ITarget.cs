#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public interface ITarget
    {
        string Name { get; set; }
        List<Object> Objects { get; set; }
    }
}
