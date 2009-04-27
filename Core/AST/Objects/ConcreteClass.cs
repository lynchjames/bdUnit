#region Using Statements

#endregion

namespace bdUnit.Core.AST
{
    public class ConcreteClass
    {
        public ConcreteClass()
        {
            Instance = new Instance();
        }

        public string Name { get; set; }
        public Instance Instance { get; set; }
    }
}