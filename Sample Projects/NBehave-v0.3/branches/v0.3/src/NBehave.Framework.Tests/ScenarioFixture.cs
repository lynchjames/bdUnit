using NBehave.Framework;
using NUnit.Framework.SyntaxHelpers;
using NUnit.Framework;

namespace NBehave.Framework.Tests
{
    [TestFixture]
    public class ScenarioFixture
    {
        [Test]
        public void Should_set_the_title_when_created()
        {
            Scenario scenario = new Story("Title").WithScenario("Scenario title");

            Assert.That(scenario.Title, Is.EqualTo("Scenario title"));
        }
    }
}
