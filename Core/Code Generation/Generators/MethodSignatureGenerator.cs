using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;

namespace bdUnit.Core.Generators
{
    public interface IMethodSignatureGenerator
    {
        string Generate(CreateMethod method);
    }

    public class MethodSignatureGenerator : GeneratorBase, IMethodSignatureGenerator
    {
        public MethodSignatureGenerator(AccessEnum access, string methodText)
        {
            Access = access;
            MethodText = methodText;
        }

        public string Generate(CreateMethod method)
        {
            var methodText = MethodText.Replace("##accesslevel##", Access.ToString());
            var _params = new StringBuilder();
            var signature = methodText.Replace("##methodname##", method.TargetMethod.Name);
            //TODO Define return type in MGrammar
            signature = signature.Replace("##returntype##", "void");
            var paramCount = method.TargetMethod.Objects.Count;
            for (var j = 1; j < paramCount; j++)
            {
                var parameter = method.TargetMethod.Objects[j];
                var instanceName = string.Empty;
                var parameterName = string.Empty;
                //TODO need to work out how to recognize List<T> method arguments (taking the first for now) - also needs to work with args list
                parameterName = !string.IsNullOrEmpty(method.TargetMethod.Relation) && j == 1
                                    ? string.Format("IList<I{0}>", method.TargetMethod.Objects[1].Name)
                                    : "I" + parameter.Name;
                if (!string.IsNullOrEmpty(parameter.Instance.Value))
                {
                    instanceName = parameter.Instance.Value;
                }
                else
                {
                    instanceName = parameter.Name.ToLower();
                }
                var delimiter = j < (paramCount - 1) ? ", " : string.Empty;
                _params.Append(string.Format("{0} {1}{2}", parameterName, instanceName, delimiter));
            }
            signature = signature.Replace("##params##", _params.ToString());
            return signature;
        }
    }
}