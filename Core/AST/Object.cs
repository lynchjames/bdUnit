﻿#region Using Statements

using System.Diagnostics;

#endregion

namespace bdUnit.Core.AST
{
    public class Object
    {
        public Object()
        {
            Instance = new Instance();
        }

        public string Name { get; set; }
        public Instance Instance { get; set; }
    }
}