#region Using Statements

using System.Linq;
using bdUnit.Core.AST;
using bdUnit.Tests.Base;
using NUnit.Framework;

#endregion

namespace bdUnit.Tests.Interfaces
{
    [TestFixture]
    public class RelationshipSignatureTests : TestBase
    {
        [Test]
        public void Test_Reciprocal_Relationship_Signature()
        {
            var input = "I want a @User to be able to #Marry another @User";
            input = CreateInput(input, null);
            Configure(input);
            var tests = _parser.Parse().ToList();
            Assert.IsNotEmpty(tests);

            var typeEntry = tests[0].TypeList[0];
            Assert.IsTrue(typeEntry.ConcreteClass.Name == "User");
            Assert.IsInstanceOf(typeof(CreateMethod), typeEntry.StatementList[0]);
            var statement = typeEntry.StatementList[0] as CreateMethod;
            Assert.AreEqual(statement.TargetMethod.ConcreteClasses.Count, 2);
        }
    }
}