#region Using Statements

#endregion

#region Using Statements

using System;
using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class If : IStatement
    {
        public If()
        {
            TargetList = new List<Target>();
        }

        public List<Target> TargetList { get; set; }
        public Then Then { get; set; }
        public Else Else { get; set; }
    }
}