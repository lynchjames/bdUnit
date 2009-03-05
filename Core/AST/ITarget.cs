using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace bdUnit.Core.AST
{
    public interface ITarget
    {
        IList<Constraint> Constraints { get; set; }
        string Name { get; set; }
        IList<Object> Objects { get; set; }
    }
}
