namespace bdUnit.Core.AST
{
    public class DefaultValue
    {
        public DefaultValue()
        {
            ConcreteClass = new ConcreteClass();
        }

        public string Value { get; set; }
        public ConcreteClass ConcreteClass { get; set; }
    }
}