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
