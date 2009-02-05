using System;
using System.Collections.Generic;
using System.Text;

namespace NBehave.Framework
{
    public class EventMessageProvider : IMessageProvider
    {
        public event EventHandler<EventArgs<string>> MessageAdded;

        protected virtual void OnMessageAdded(EventArgs<string> e)
        {
            EventHandler<EventArgs<string>> handler = MessageAdded;
            if (handler != null)
                handler(this, e);
        }

        void IMessageProvider.AddMessage(string message)
        {
            OnMessageAdded(new EventArgs<string>(message));
        }
    }
}
