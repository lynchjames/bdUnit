#region Using Statements

using System.Diagnostics;

#endregion

namespace bdUnit.Core.AST
{
    public class Object
    {
        public string Name { get; set; }
        public string Instance { get; set; }

        public void Print()
        {
            Debug.WriteLine("\t\tI am Object -- Name: " + Name + " InstanceName: " + Instance);
        }
    }
}