#region Using Statements

using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Forms;
using System.Windows.Forms.Integration;
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

        #region Events

        private void Window1_Loaded(object sender, RoutedEventArgs e)
        {
            Closing += Window1_Closing;
            EventBus.TextChanged += EventBus_TextChanged;
        }

        private void EventBus_TextChanged(object sender, EventArgs e)
        {
            var id = ((TargetEventArgs)e).TargetId;
            var tabs = tabControl.Items;
            var tabCount = tabs.Count;
            for (int i = 0; i < tabCount; i++)
            {
                var tab = tabs[i] as TabItem;
                if (tab != null && ((bdUnitPreviewWindow)tab.Content).Id == id && !((TextBlock)tab.Header).Text.Contains("*"))
                {
                    var header = ((TextBlock)tab.Header);
                    header.Text = header.Text + "*";
                    header.FontWeight = FontWeights.Bold;
                }
            }
        }

        void Window1_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            try
            {
                for (int i = 0; i < tabControl.Items.Count; i++)
                {
                    var item = tabControl.Items[i] as TabItem;
                    var bdUnitPreviewWindow1 = ((bdUnitPreviewWindow)item.Content);
                    bdUnitPreviewWindow1.Dispose();
                }
            }
            catch (Exception ex)
            {

            }
        }

        void Window1_Closed(object sender, EventArgs e)
        {
            try
            {
                //for (int i = 0; i < tabControl.Items.Count; i++)
                //{
                //    var item = tabControl.Items[i];
                //    var bdUnitPreviewWindow1 = ((bdUnitPreviewWindow)item);
                //    bdUnitPreviewWindow1.Dispose();
                //}
            }
            catch (Exception)
            {

            }
        }

        private void Command_Executed(object sender, ExecutedRoutedEventArgs e)
        {
            var command = (RoutedUICommand)e.Command;
            switch (command.Text)
            {
                case "New":
                    var tab = new TabItem { Header = "New Tab", Content = new bdUnitPreviewWindow() };
                    tabControl.Items.Add(tab);
                    tabControl.SelectedIndex = tabControl.Items.Count - 1;
                    break;
                case "Open":
                    var fileDialog = new OpenFileDialog { Multiselect = true };
                    if (fileDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                    {
                        var filePaths = fileDialog.FileNames;
                        var fileNames = fileDialog.SafeFileNames;
                        var fileCount = filePaths.Length;
                        for (var i = 0; i < fileCount; i++)
                        {
                            var bdUnitPreview = new bdUnitPreviewWindow(filePaths[i], Menu.CurrentFramework)
                            {
                                CurrentTabIndex = tabControl.Items.Count,
                                FilePath = filePaths[i],
                                FileName = fileNames[i]
                            };
                            var openTab = new TabItem { Header = new TextBlock { Text = fileNames[i] }, Content = bdUnitPreview, IsSelected = true };
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
                    //TODO Add save for new docs
                    var preview = ((TabItem)tabControl.SelectedItem).Content as bdUnitPreviewWindow;
                    if (preview != null && !preview.IsSaved)
                    {
                        var range = new TextRange(preview.InputEditor.Document.ContentStart, preview.InputEditor.Document.ContentEnd);
                        var text = range.Text;
                        File.WriteAllText(preview.FilePath, text);
                        preview.IsSaved = true;
                        var header = ((TabItem)tabControl.SelectedItem).Header as TextBlock;
                        if (header != null)
                        {
                            header.Text = preview.FileName;
                            header.FontWeight = FontWeights.Normal;
                        }
                    }
                    break;
            }
        }

        #endregion Events

        private void Command_CanExecute(object sender, CanExecuteRoutedEventArgs e)
        {
            //TODO Add required check to prevent new tab menu option
            e.CanExecute = true;
        }

        private void ContextMenu_Click(object sender, RoutedEventArgs e)
        {
            
        }
    }
}