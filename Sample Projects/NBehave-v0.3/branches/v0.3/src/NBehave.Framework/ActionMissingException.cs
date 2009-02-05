using System;
using System.Runtime.Serialization;

namespace NBehave.Framework
{
    public class ActionMissingException : Exception
    {
        public ActionMissingException() : base() { }
        public ActionMissingException(string message) : base(message) { }
        public ActionMissingException(string message, Exception innerException) : base(message, innerException) { }
        public ActionMissingException(SerializationInfo info, StreamingContext context) : base(info, context) { }
    }
}
