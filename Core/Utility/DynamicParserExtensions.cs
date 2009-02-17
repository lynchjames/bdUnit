using System;
using System.Collections.Generic;
using System.Dataflow;
using System.Linq;
using System.Text;
using Gallio.Framework;
using MbUnit.Framework;

namespace bdUnit.Core.Utility
{
    public partial class DynamicParserExtensions
    {
        internal class ExceptionErrorReporter : ErrorReporter
        {
            protected override void OnError(ISourceLocation sourceLocation, ErrorInformation errorInformation)
            {
                var eventArgs = errorInformation.ToBuildEventArgs(sourceLocation, String.Empty, String.Empty);
                throw new Exception(String.Format("Parser Exception: {0}", eventArgs));
            }
        }
    }
}
