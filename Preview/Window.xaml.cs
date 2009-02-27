#region Using Statements

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Text;
using System.Threading;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Forms.Integration;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using bdUnit.Core;
using bdUnit.Core.Utility;
using bdUnit.Preview.Controls;
using Core.Enum;
using ScintillaNet;
using Brushes=System.Windows.Media.Brushes;
using Image=System.Windows.Controls.Image;
using TextRange=System.Windows.Documents.TextRange;
using Timer=System.Timers.Timer;

#endregion

namespace Preview
{
    /// <summary>
    /// Interaction logic for Window1.xaml
    /// </summary>
    public partial class Window1
    {
        public Window1()
        {
            InitializeComponent();
            Loaded += Window1_Loaded;
            //tabControl.TabItemAdded += tabControl_TabItemAdded;
        }

        private void Window1_Loaded(object sender, RoutedEventArgs e)
        {
            Closed += Window1_Closed;
        }

        void Window1_Closed(object sender, EventArgs e)
        {
            try
            {
                //for (int i = 0; i < tabControl.Items.Count; i++)
                //{
                //    var item = tabControl.Items[i];
                //    var host = ((bdUnitPreviewWindow)item).Preview.Content as WindowsFormsHost;
                //    host.Dispose();
                //}
            }
            catch (Exception)
            {

            }
        }
    }
}
