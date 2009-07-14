using bdUnit.Core.Utility;
using bdUnit.Tests.Base;
using NUnit.Framework;
using System.Linq;

namespace bdUnit.Tests.Interfaces
{
    [TestFixture]
    public class DefaultValueTests : TestBase
    {
        [Test]
        public void String_Default_Value_Signature_Should_Parse_To_Test_List()
        {
            var input = "and a ~FirstName";
            CreateInputAndConfigure(input, null, "Person");
            ParseTest();
        }

        [Test]
        public void String_Default_Value_Signature_With_String_Included_Should_Parse_To_Test_List()
        {
            var input = "and a ~FirstName(James)";
            CreateInputAndConfigure(input, null, "Person");
            ParseTest();
        }

        [Test]
        public void String_Default_Value_Signature_With_String_Included_Should_Have_Regex_Match()
        {
            var input = "and a ~FirstName(James)";
            CreateInputAndConfigure(input, null, "Person");
            var test = _parser.Parse().ElementAt(0);
            var defaultValue = test.TypeList[0].PropertyList[1].DefaultValue.Value;
            Assert.IsTrue(RegexUtility.IsString(defaultValue));
        }

        [Test]
        public void DateTime_Default_Value_Signature_Should_Parse_To_Test_List()
        {
            var input = "and a ~DateOfBirth(\"22/04/1983\")";
            CreateInputAndConfigure(input, null, "Person");
            ParseTest();
        }

        [Test]
        public void DateTime_Default_Value_Signature_Should_Have_Regex_Match()
        {
            var input = "and a ~DateOfBirth(\"22/04/1983\")";
            CreateInputAndConfigure(input, null, "Person");
            var test = _parser.Parse().ElementAt(0);
            var defaultValue = test.TypeList[0].PropertyList[1].DefaultValue.Value;
            Assert.IsTrue(RegexUtility.IsDateTime(defaultValue));
        }

        [Test]
        public void Short_DateTime_Default_Value_Signature_Should_Have_Regex_Match()
        {
            var input = "and a ~DateOfBirth(\"1st Jan 2001\")";
            CreateInputAndConfigure(input, null, "Person");
            var test = _parser.Parse().ElementAt(0);
            var defaultValue = test.TypeList[0].PropertyList[1].DefaultValue.Value;
            Assert.IsTrue(RegexUtility.IsDateTime(defaultValue));
        }

        [Test]
        public void DateTime_In_US_Format_Default_Value_Signature_Should_Have_Regex_Match()
        {
            var input = "and a ~DateOfBirth(\"04/22/1983\")";
            CreateInputAndConfigure(input, null, "Person");
            var test = _parser.Parse().ElementAt(0);
            var defaultValue = test.TypeList[0].PropertyList[1].DefaultValue.Value;
            Assert.IsTrue(RegexUtility.IsDateTime(defaultValue));
        }

        [Test]
        public void Boolean_Default_Value_Signature_Should_Parse_To_Test_List()
        {
            var input = "and a ~IsDead(false)";
            CreateInputAndConfigure(input, null, "Person");
            ParseTest();
        }

        [Test]
        public void Boolean_Default_Value_Signature_Should_Have_Regex_Match()
        {
            var input = "and a ~IsDead(false)";
            CreateInputAndConfigure(input, null, "Person");
            var test = _parser.Parse().ElementAt(0);
            var defaultValue = test.TypeList[0].PropertyList[1].DefaultValue.Value;
            Assert.IsTrue(RegexUtility.IsBool(defaultValue));
        }

        [Test]
        public void Integer_Default_Value_Signature_Should_Parse_To_Test_List()
        {
            var input = "and an ~Age(26)";
            CreateInputAndConfigure(input, null, "Person");
            ParseTest();
        }

        [Test]
        public void Integer_Default_Value_Signature_Should_Have_Regex_Match()
        {
            var input = "and an ~Age(26)";
            CreateInputAndConfigure(input, null, "Person");
            var test = _parser.Parse().ElementAt(0);
            var defaultValue = test.TypeList[0].PropertyList[1].DefaultValue.Value;
            Assert.IsTrue(RegexUtility.IsInteger(defaultValue));
        }

        [Test]
        public void Double_Default_Value_Signature_Should_Parse_To_Test_List()
        {
            var input = "and a ~Height(1.778)";
            CreateInputAndConfigure(input, null, "Person");
            ParseTest();
        }

        [Test]
        public void Double_Default_Value_Signature_Should_Have_Regex_Match()
        {
            var input = "and a ~Height(1.778)";
            CreateInputAndConfigure(input, null, "Person");
            var test = _parser.Parse().ElementAt(0);
            var defaultValue = test.TypeList[0].PropertyList[1].DefaultValue.Value;
            Assert.IsTrue(RegexUtility.IsDouble(defaultValue));
        }
    }
}