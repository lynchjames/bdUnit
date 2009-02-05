using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace bdUnit.Core.AST
{
    public class DefaultValue
    {
        public DefaultValue()
        {
            Object = new Object();
        }

        public string Value { get; set; }
        public Object Object { get; set; }
    }
}
