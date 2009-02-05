using System;

namespace NBehave.Framework
{
    public class EventArgs<T> : EventArgs
    {
        private T _eventData;

        public EventArgs(T eventData)
        {
            _eventData = eventData;
        }

        public T EventData
        {
            get { return _eventData; }
        }
    }
}
