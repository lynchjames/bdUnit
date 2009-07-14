using bdUnit.Core.Enum;
using bdUnit.Tests.Base;
using NUnit.Framework;
using System.Linq;

namespace bdUnit.Tests.Interfaces
{
    [TestFixture]
    public class CollectionSignatureTests : TestBase
    {
        [Test]
        public void Collection_Signature_Should_Parse_To_Test_List()
        {
            var input = "and several ~Children(@Person)";
            CreateInputAndConfigure(input, null, "Person");
            ParseTest();
        }

        [Test]
        public void Collection_Signature_Should_Have_ManyToOne_Relation()
        {
            var input = "and several ~Children(@Person)";
            CreateInputAndConfigure(input, null, "Person");
            var test = _parser.Parse().ElementAt(0);
            var property = test.TypeList[0].PropertyList[1];
            Assert.AreEqual(property.GetRelationQualifiedEnum(), RelationQualifiedEnum.ManyToOne);
        }

        [Test]
        public void Collection_Signature_Should_Have_ConcreteClass_As_DefaultValue()
        {
            var input = "and several ~Children(@Person)";
            CreateInputAndConfigure(input, null, "Person");
            var test = _parser.Parse().ElementAt(0);
            var property = test.TypeList[0].PropertyList[1];
            var concreteClass = property.DefaultValue.ConcreteClass;
            Assert.IsNotNull(concreteClass);
            Assert.AreEqual(concreteClass.Name, "Person");
        }
    }
}