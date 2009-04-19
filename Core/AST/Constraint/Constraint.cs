﻿#region Using Statements



#endregion

#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class Constraint
    {
        public Constraint()
        {
            Property = new Property();
            Objects = new List<ConcreteClass>();
            Operators = new List<Operator>();
        }

        public List<ConcreteClass> Objects { get; set; }
        public List<Operator> Operators { get; set; }
        public Property Property { get; set; }
    }
}