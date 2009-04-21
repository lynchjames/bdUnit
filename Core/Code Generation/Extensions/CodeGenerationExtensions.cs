using bdUnit.Core.AST;

namespace bdUnit.Core.Extensions
{
  public static class CodeGenerationExtensions
  {
      public static string AsStructureMapInstance(this ConcreteClass @class)
      {
        return string.Format("\t\t\tI{1} {0} = ObjectFactory.GetInstance<I{1}>();\n", @class.Instance.Value, @class.Name);
      }
  }
}