using System;
using System.Collections.Generic;
using System.Text;
using System.ComponentModel;

namespace Wpf.Controls
{
    public class TabItemEventArgs : EventArgs
    {
        TabItem _item;

        public TabItem TabItem
        {
            get { return _item; }
        }

        public TabItemEventArgs(TabItem item)
        {
            _item = item;
        }
    }

    public class TabItemCancelEventArgs : CancelEventArgs
    {
        TabItem _item;

        public TabItem TabItem
        {
            get { return _item; }
        }

        public TabItemCancelEventArgs(TabItem item)
            : base()
        {
            _item = item;
        }
    }
}
