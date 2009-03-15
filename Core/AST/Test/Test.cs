#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class Test
    {
        public Test()
        {
            StatementList = new List<IStatement>();
            TypeList = new List<Type>();
        }

        public List<Type> TypeList { get; set; }
        public List<IStatement> StatementList { get; private set; }
        public string Title { get; set; }
    }
}