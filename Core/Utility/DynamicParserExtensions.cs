#region Using Statements

using System;
using System.Dataflow;

#endregion

namespace bdUnit.Core.Utility
{
    public class DynamicParserExtensions
    {
        #region Nested type: ErrorException

        public class ErrorException : Exception
        {
            public ErrorException(ISourceLocation location, ErrorInformation information)
            {
                Error = information;
                Location = location;
            }

            public ErrorInformation Error { get; set; }
            public ISourceLocation Location { get; set; }

            public override string Message
            {
                get { return Error.ToBuildEventArgs(Error.Arguments.ToString(), "").Message; }
            }
        }

        #endregion

        #region Nested type: ExceptionErrorReporter

        internal class ExceptionErrorReporter : ErrorReporter
        {
            protected override void OnError(ErrorInformation errorInformation)
            {
                throw new ErrorException(errorInformation.Location, errorInformation);
            }
        }

        #endregion
    }
}