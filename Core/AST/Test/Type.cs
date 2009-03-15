#region Using Statements

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
        public List<IStatement> StatementList { get; private set; }
        public List<Property> PropertyList { get; set; }
    }
}