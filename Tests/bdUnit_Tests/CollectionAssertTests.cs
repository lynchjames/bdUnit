using bdUnit.Core.AST;
using bdUnit.Core.Enum;
using bdUnit.Tests.Base;
using NUnit.Framework;
using System.Linq;

namespace bdUnit.Tests.Tests
{
    [TestFixture]
    public class CollectionAssertTests : TestBase
    {
        [Test]
        public void Collection_Assert_Should_Parse_To_Test_List()
        {
            var input = @"When a @Person(user) ~UnMarried is (true)
	                        @Person(user) should have less than 3 ~Children";
            CreateInputAndConfigure(null, input, "Person");
            ParseTest();
        }

        [Test]
        public void Collection_Assert_With_Count_And_Less_Than_Operator_And_Value()
        {
            var input = @"When a @Person(user) ~UnMarried is (true)
	                        @Person(user) should have less than 3 ~Children";
            CreateInputAndConfigure(null, input, "Person");
            Assert.IsNotNull(Constraint.Property.Count);
            Assert.AreEqual(int.Parse(Constraint.Property.Count.Value), 3);
            Assert.AreEqual(Constraint.Property.Count.Operators[0].Value, "<");
        }

        [Test]
        public void Collection_Assert_With_Count_And_Greater_Than_Operator_And_Value()
        {
            var input = @"When a @Person(user) ~UnMarried is (true)
	                        @Person(user) should have more than 1 ~Children";
            CreateInputAndConfigure(null, input, "Person");
            Assert.IsNotNull(Constraint.Property.Count);
            Assert.AreEqual(int.Parse(Constraint.Property.Count.Value), 1);
            Assert.AreEqual(Constraint.Property.Count.Operators[0].Value, ">");
        }

        [Test]
        public void Collection_Assert_With_Count_And_Equals_Operator_And_Value()
        {
            var input = @"When a @Person(user) ~UnMarried is (true)
	                        @Person(user) should have 2 ~Children";
            CreateInputAndConfigure(null, input, "Person");
            Assert.IsNotNull(Constraint.Property.Count);
            Assert.AreEqual(int.Parse(Constraint.Property.Count.Value), 2);
            Assert.AreEqual(Constraint.Property.Count.Operators[0].Value, "==");
        }

        [Test]
        public void Collection_Assert_With_Contains_And_Value()
        {
            var input = @"When a @Person(user) ~UnMarried is (true)
	                        @Person(user) ~Children should contain @User(user1)";
            CreateInputAndConfigure(null, input, "Person");
            Assert.IsNotNull(Constraint.ConcreteClassPropertyMapping);
            Assert.AreEqual(Constraint.ConcreteClassPropertyMapping.ConcreteClasses, 2);
            Assert.AreEqual(Constraint.Operators[0].Value, "contains");
        }
    }
}