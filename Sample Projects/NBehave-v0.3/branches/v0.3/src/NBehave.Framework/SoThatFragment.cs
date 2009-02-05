using System.Diagnostics;

namespace NBehave.Framework
{
    public class SoThatFragment
    {
        private readonly Story _story;

        internal SoThatFragment(string benefit, Story story)
        {
            Debug.Assert(story != null);

            _story = story;

            _story.AddMessage("\tSo that " + benefit);
        }

        public Scenario WithScenario(string title)
        {
            return _story.WithScenario(title);
        }
    }
}
