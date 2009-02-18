using System;
using System.Collections;
using System.Dataflow;
using System.Runtime.Serialization;

namespace bdUnit.Core.Utility
{
    public partial class DynamicParserExtensions
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
                this.Error = information;
                this.Location = location;
            }

            public override Exception GetBaseException()
            {
                return base.GetBaseException();
            }

            public override void GetObjectData(SerializationInfo info, StreamingContext context)
            {
                base.GetObjectData(info, context);
            }

            public override string Message
            {
                get { return Error.ToBuildEventArgs(Location, String.Empty, String.Empty).Message; }
            }

            public override string StackTrace
            {
                get { return base.StackTrace; }
            }

            public override string HelpLink
            {
                get { return base.HelpLink; }
                set { base.HelpLink = value; }
            }

            public override string Source
            {
                get { return base.Source; }
                set { base.Source = value; }
            }

            public override IDictionary Data
            {
                get { return base.Data; }
            }

            public override string ToString()
            {
                return base.ToString();
            }
        }
    }
}
