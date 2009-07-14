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
        public void Reciprocal_Relationship_Signature_Should_Parse_To_Test_List()
        {
            var input = "I want a @User to be able to #Marry another @User";
            CreateInputAndConfigure(input, null, "User");
            ParseTest();
        }

        [Test]
        public void Reciprocal_Relationship_Signature_Should_Have_Correct_ConcreteClass()
        {
            var input = "I want a @User to be able to #Marry another @User";
            CreateInputAndConfigure(input, null, "User");
            var tests = _parser.Parse().ToList();
            var typeEntry = tests[0].TypeList[0];
            Assert.IsTrue(typeEntry.ConcreteClass.Name == "User");
        }

        [Test]
        public void Reciprocal_Relationship_Signature_Should_Be_CreateMethod_With_Two_ConcreteClasses()
        {
            var input = "I want a @User to be able to #Marry another @User";
            CreateInputAndConfigure(input, null, "User");
            var tests = _parser.Parse().ToList();
            var typeEntry = tests[0].TypeList[0];
            Assert.IsInstanceOf(typeof(CreateMethod), typeEntry.StatementList[0]);
            var statement = typeEntry.StatementList[0] as CreateMethod;
            Assert.AreEqual(statement.TargetMethod.ConcreteClasses.Count, 2);
        }
    }
}