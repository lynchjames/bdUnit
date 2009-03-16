#region Using Statements

using System.Linq;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;

#endregion

namespace bdUnit.Core.Generators
{
    public interface IInterfaceGenerator
    {
        string Generate(Type type);
    }

    public class InterfaceGenerator : GeneratorBase, IInterfaceGenerator
    {
        private readonly MethodSignatureGenerator _methodSignatureGenerator;
        private readonly PropertyGenerator _propertyGenerator;

        public InterfaceGenerator(AccessEnum access, string typeText, 
            IMethodSignatureGenerator methodSigGenerator, IPropertyGenerator propertyGenerator)
        {
            Access = access;
            TypeText = typeText;
            _methodSignatureGenerator = methodSigGenerator as MethodSignatureGenerator;
            _propertyGenerator = propertyGenerator as PropertyGenerator;
        }

        public string Generate(Type type)
        {
            var wrapper = TypeText.Replace("##accesslevel##", Access.ToString()).Replace("##typename##",
                                                                                            type.Object.Name);
            var properties = type.PropertyList;
            var content = new StringBuilder();
            content.Append(_propertyGenerator.Generate(properties));
            var methodStatments =
                type.StatementList.Where(s => s.GetType().Name == "CreateMethod").ToList();
            methodStatments.ForEach(ms => content.AppendLine(_methodSignatureGenerator.Generate((CreateMethod)ms)));
            wrapper = wrapper.Replace("##content##", content.ToString());
            return wrapper;
        }
    }
}