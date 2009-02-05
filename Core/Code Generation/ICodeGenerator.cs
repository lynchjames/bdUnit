using System.Collections.Generic;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;

namespace bdUnit.Core
{
    public interface ICodeGenerator
    {
        #region Properties
        
        AccessEnum Access { get; set; } 
        
        #endregion

        #region Methods

        string GenerateTestFixture(List<Test> tests, string fileName);
        string GenerateTest(Test test, string path, AccessEnum access);
        StringBuilder GenerateMethods(IList<IStatement> statements, StringBuilder stringBuilder);
        string GenerateInterfaces(Type type);
        string GenerateProperties(IList<Property> properties);
        string GenerateMethodSignature(CreateMethod method);
        string GenerateAsserts(Object _object, IList<Constraint> constraints);

        #endregion
    }
}