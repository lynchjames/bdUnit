#region Using Statements

using System.Collections.Generic;
using bdUnit.Core.AST;
using bdUnit.Core.Enum;

#endregion

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

        #endregion
    }
}