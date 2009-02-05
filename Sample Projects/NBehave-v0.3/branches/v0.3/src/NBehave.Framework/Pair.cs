using System;
using System.Runtime.InteropServices;
using System.Text;

namespace NBehave.Framework
{
    [Serializable, StructLayout(LayoutKind.Sequential)]
    public struct Pair<T1, T2>
    {
        private T1 _first;
        private T2 _second;

        public Pair(T1 first, T2 second)
        {
            _first = first;
            _second = second;
        }

        public T1 First
        {
            get { return _first; }
        }

        public T2 Second
        {
            get { return _second; }
        }

        public override string ToString()
        {
            StringBuilder builder = new StringBuilder();
            builder.Append('[');
            if (First != null)
            {
                builder.Append(First.ToString());
            }
            builder.Append(", ");
            if (Second != null)
            {
                builder.Append(Second.ToString());
            }
            builder.Append(']');
            return builder.ToString();
        }

    }
}
