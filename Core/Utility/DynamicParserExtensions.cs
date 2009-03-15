#region Using Statements

using System;
using System.Collections;
using System.Dataflow;
using System.Runtime.Serialization;

#endregion

namespace bdUnit.Core.Utility
{
    public class DynamicParserExtensions
    {
        internal class ExceptionErrorReporter : ErrorReporter
        {
            protected override void OnError(ISourceLocation sourceLocation, ErrorInformation errorInformation)
            {
                throw new ErrorException(sourceLocation, errorInformation);
            }
        }



        public class ErrorException : Exception
        {
            public ErrorInformation Error { get; set; }
            public ISourceLocation Location { get; set; }

            public ErrorException(ISourceLocation location, ErrorInformation information)
            {
                Error = information;
                Location = location;
            }

            public override string Message
            {
                get { return Error.ToBuildEventArgs(Location, String.Empty, String.Empty).Message; }
            }
        }
    }
}
