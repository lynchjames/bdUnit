#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class TargetMethod : ITarget
    {
        public TargetMethod()
        {
            Objects = new List<Object>();
            Properties = new List<Property>();
        }

        public string Name { get; set; }
        public IList<Object> Objects { get; set; }
        public IList<Property> Properties { get; set; }
        public Loop Loop { get; set; }
    }
}