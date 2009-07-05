#region Using Statements

using System;
using System.Dataflow;

#endregion

namespace bdUnit.Core.Utility
{
    public class DynamicParserExtensions
    {
        #region Nested type: ParserErrorException

        public class ParserErrorException : Exception
        {
            public ParserErrorException(ISourceLocation location, ErrorInformation information)
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
                throw new ParserErrorException(errorInformation.Location, errorInformation);
            }
        }

        #endregion
    }
}