using System;

namespace NBehave.Framework
{
    public class DisposableAction : IDisposable
    {
        private readonly Action _disposeAction;

        public DisposableAction(Action disposeAction)
        {
            _disposeAction = disposeAction;
        }

        public void Dispose()
        {
            _disposeAction();
        }
    }
}
