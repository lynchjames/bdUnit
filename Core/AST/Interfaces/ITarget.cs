#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public interface ITarget
    {
        string Name { get; set; }
        List<ConcreteClass> ConcreteClasses { get; set; }
    }
}