#region Using Statements

using System;
using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class Type
    {
        public Type()
        {
            PropertyList = new List<Property>();
            StatementList = new List<IStatement>();
        }

        public Object Object { get; set; }
        public IList<IStatement> StatementList { get; private set; }
        public IList<Property> PropertyList { get; set; }
    }
}