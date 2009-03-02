#region Using Statements

using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Forms;
using System.Windows.Input;
using bdUnit.Preview.Code;
using bdUnit.Preview.Controls;
using TextRange=System.Windows.Documents.TextRange;

#endregion

namespace bdUnit.Preview
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
            EventBus.TextChanged += EventBus_TextChanged;
        }

        private void EventBus_TextChanged(object sender, EventArgs e)
        {
            var id = ((TargetEventArgs) e).TargetId;
            var tabs = tabControl.Items;
            var tabCount = tabs.Count;
            for (int i = 0; i < tabCount; i++)
            {
                var tab = tabs[i] as TabItem;
                if (tab != null && ((bdUnitPreviewWindow)tab.Content).Id == id && !((TextBlock)tab.Header).Text.Contains("*"))
                {
                    var header = ((TextBlock)tab.Header);
                    header.Text =  header.Text + " *";
                    header.FontWeight = FontWeights.Bold;
                }
            }
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

        private void Command_Executed(object sender, ExecutedRoutedEventArgs e)
        {
            var command = (RoutedUICommand) e.Command;
            switch (command.Text)
            {
                case "New":
                    var tab = new TabItem {Header = "New Tab", Content = new bdUnitPreviewWindow()};
                    tabControl.Items.Add(tab);
                    break;
                case "Open":
                    var fileDialog = new OpenFileDialog();
                    fileDialog.Multiselect = true;
                    if (fileDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                    {
                        var filePaths = fileDialog.FileNames;
                        var fileNames = fileDialog.SafeFileNames;
                        var fileCount = filePaths.Length;
                        for (int i = 0; i < fileCount; i++)
                        {
                            var bdUnitPreview = new bdUnitPreviewWindow(filePaths[i], Menu.CurrentFramework);
                            bdUnitPreview.CurrentTabIndex = tabControl.Items.Count;
                            bdUnitPreview.FilePath = filePaths[i];
                            bdUnitPreview.FileName = fileNames[i];
                            var openTab = new TabItem { Header = new TextBlock {Text = fileNames[i]}, Content = bdUnitPreview, IsSelected = true};
                            tabControl.Items.Add(openTab);
                            tabControl.SelectedIndex = tabControl.Items.Count - 1;
                        }
                    }
                    break;
                case "Close":
                    var currentTab = tabControl.SelectedItem;
                    tabControl.Items.Remove(currentTab);
                    break;
                case "Save":
                    var preview = ((TabItem)tabControl.SelectedItem).Content as bdUnitPreviewWindow;
                    if (preview != null && !preview.IsSaved)
                    {
                        var range = new TextRange(preview.InputEditor.Document.ContentStart, preview.InputEditor.Document.ContentEnd);
                        var text = range.Text;
                        File.WriteAllText(preview.FilePath, text);
                        preview.IsSaved = true;
                        var header = ((TabItem) tabControl.SelectedItem).Header as TextBlock;
                        if (header != null)
                        {
                            header.Text = preview.FileName;
                            header.FontWeight = FontWeights.Normal; 
                        }
                    }
                    break;
            }
        }

        private void Command_CanExecute(object sender, CanExecuteRoutedEventArgs e)
        {
            //TODO Add required check to prevent new tab menu option
            e.CanExecute = true;
        }
    }
}