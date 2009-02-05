using System;
using System.Text;

namespace NBehave.Framework
{
    public class ScenarioResults
    {
        private readonly string _storyTitle;
        private readonly string _scenarioTitle;
        private ScenarioResult _scenarioResult;
        private string _message = null;
        private string _stackTrace;

        public ScenarioResults(string storyTitle, string scenarioTitle) : this(storyTitle, scenarioTitle, ScenarioResult.Passed)
        {
        }

        public ScenarioResults(string storyTitle, string scenarioTitle, ScenarioResult scenarioResult)
        {
            _storyTitle = storyTitle;
            _scenarioTitle = scenarioTitle;
            _scenarioResult = scenarioResult;
        }

        public string StoryTitle
        {
            get { return _storyTitle; }
        }

        public string ScenarioTitle
        {
            get { return _scenarioTitle; }
        }

        public ScenarioResult ScenarioResult
        {
            get { return _scenarioResult; }
        }

        public string Message
        {
            get { return _message; }
        }

        public string StackTrace
        {
            get { return _stackTrace; }
        }

        public void Fail(Exception exception)
        {
            _scenarioResult = ScenarioResult.Failed;
            _message = BuildMessage(exception);
            _stackTrace = BuildStackTrace(exception);
        }

        public void Pend(string reason)
        {
            _scenarioResult = ScenarioResult.Pending;
            _message = reason;
        }

        private string BuildMessage(Exception exception)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendFormat("{0} : {1}", exception.GetType(), exception.Message);

            Exception inner = exception.InnerException;
            while (inner != null)
            {
                sb.AppendLine();
                sb.AppendFormat("  ----> {0} : {1}", inner.GetType(), inner.Message);
                inner = inner.InnerException;
            }

            return sb.ToString();
        }

        private string BuildStackTrace(Exception exception)
        {
            StringBuilder builder = new StringBuilder(exception.StackTrace);

            Exception inner = exception.InnerException;
            while (inner != null)
            {
                builder.AppendLine();
                builder.Append("--");
                builder.Append(inner.GetType().Name);
                builder.AppendLine();
                builder.Append(inner.StackTrace);
                inner = inner.InnerException;
            }
            return builder.ToString();
        }
    }
}
