#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class ConcreteClassPropertyMapping
    {
        public ConcreteClassPropertyMapping()
        {
            ConcreteClasses = new List<ConcreteClass>();
            Properties = new List<Property>();
        }

        public List<ConcreteClass> ConcreteClasses { get; set; }
        public List<Property> Properties { get; set; }
    }
}