using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using bdUnit.Preview.Code;
using Core.Enum;

namespace bdUnit.Preview.Controls
{
    /// <summary>
    /// Interaction logic for MenuToolbar.xaml
    /// </summary>
    public partial class MenuToolbar
    {
        public UnitTestFrameworkEnum CurrentFramework { get; set; }

        private List<MenuItem> FrameworkMenuItems
        {
            get
            {
                return new List<MenuItem>() { NUnit, XUnit, MbUnit };
            }
        }

        public MenuToolbar()
        {
            InitializeComponent();
            Loaded += MenuToolbar_Loaded;
        }

        void MenuToolbar_Loaded(object sender, RoutedEventArgs e)
        {
            NUnit.IsChecked = true;
        }

        private void Framework_Checked(object sender, RoutedEventArgs e)
        {
            var menuItem = (MenuItem) sender;
            FrameworkMenuItems.Where(mi => mi.Name != menuItem.Name).ToList().ForEach(mi => mi.IsChecked = false);
            CurrentFramework = (UnitTestFrameworkEnum)Enum.Parse(typeof(UnitTestFrameworkEnum), menuItem.Name);
            EventBus.OnFrameworkChecked(this, new EventArgs());
        }
    }
}
