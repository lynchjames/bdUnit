﻿#region Using Statements

using System.Collections.Generic;

#endregion

namespace bdUnit.Core.AST
{
    public class Loop : IStatement
    {
        public Loop()
        {
            Constraints = new List<Constraint>();
            Objects = new List<Object>();
        }

        public List<Object> Objects { get; set; }
        public List<Constraint> Constraints { get; set; }

        #region IStatement Members

        public TargetMethod TargetMethod { get; set; }

        #endregion
    }
}