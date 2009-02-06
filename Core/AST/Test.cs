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

        public IList<Type> TypeList { get; set; }
        public IList<IStatement> StatementList { get; private set; }
        public string Title { get; set; }
    }
}