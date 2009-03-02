#region Using Statements

using System;
using System.Collections.Generic;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Forms;
using System.Windows.Forms.Integration;
using System.Windows.Input;
using bdUnit.Preview.Code;
using bdUnit.Preview.Controls;
using ContextMenu=System.Windows.Controls.ContextMenu;
using MenuItem=System.Windows.Controls.MenuItem;
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
            EventBus.AppExit += EventBus_AppExit;
        }

        private void EventBus_AppExit(object sender, EventArgs e)
        {
            Close();
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

        private void Command_Executed(object sender, ExecutedRoutedEventArgs e)
        {
            var command = (RoutedUICommand)e.Command;
            switch (command.Text)
            {
                case "New":
                    var tab = new TabItem { Header = new TextBlock(){Text = "[Untitled]", TextTrimming = TextTrimming.CharacterEllipsis, TextWrapping = TextWrapping.NoWrap}, Content = new bdUnitPreviewWindow()};
                    tab.ContextMenu = GenerateContextMenu(tab);
                    tabControl.Items.Add(tab);
                    tabControl.SelectedIndex = tabControl.Items.Count - 1;
                    break;
                case "Open":
                    var openFileDialog = new OpenFileDialog
                                             {
                                                 Multiselect = true,
                                                 Filter = "Input text | *.input",
                                                 RestoreDirectory = true
                                             };
                    if (openFileDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                    {
                        var filePaths = openFileDialog.FileNames;
                        var fileNames = openFileDialog.SafeFileNames;
                        var fileCount = filePaths.Length;
                        for (var i = 0; i < fileCount; i++)
                        {
                            var bdUnitPreview = new bdUnitPreviewWindow(filePaths[i], Menu.CurrentFramework)
                            {
                                CurrentTabIndex = tabControl.Items.Count,
                                FilePath = filePaths[i],
                                FileName = fileNames[i]
                            };
                            var openTab = new TabItem { Header = new TextBlock { Text = fileNames[i], TextTrimming = TextTrimming.CharacterEllipsis, TextWrapping = TextWrapping.NoWrap }, Content = bdUnitPreview, IsSelected = true };
                            openTab.ContextMenu = GenerateContextMenu(openTab);
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
                        if (string.IsNullOrEmpty(preview.FilePath))
                        {
                            var saveFileDialog = new SaveFileDialog()
                                                     {Filter = "Input text | *.input", RestoreDirectory = true};
                            if (saveFileDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                            {
                                preview.FilePath = saveFileDialog.FileName;
                                var pathParts = saveFileDialog.FileName.Split('\\');
                                preview.FileName = pathParts[pathParts.Length - 1];
                            }
                        }
                        if (File.Exists(preview.FilePath))
                        {
                            File.WriteAllText(preview.FilePath, text);   
                        }
                        else
                        {
                            var info = new FileInfo(preview.FilePath);
                            StreamWriter writer = info.CreateText();
                            writer.Write(text);
                            writer.Close();
                        }
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

        private ContextMenu GenerateContextMenu(TabItem tab)
        {
            var contextMenu = new ContextMenu() {PlacementTarget = tab };
            var close = new MenuItem() {Header = "Close", Command = ApplicationCommands.Close};
            var closeAll = new MenuItem() {Header = "Close All", Name = "CloseAll"};
            var closeAllBut = new MenuItem() {Header = "Close All But This", Name = "CloseAllButThis"};
            var menus = new List<MenuItem>() {close, closeAll, closeAllBut};
            menus.ForEach(m =>
                              {
                                  m.Click += ContextMenu_Click;
                                  contextMenu.Items.Add(m);
                              });
            return contextMenu;
        }

        #endregion Events

        private void Command_CanExecute(object sender, CanExecuteRoutedEventArgs e)
        {
            //TODO Add required check to prevent new tab menu option
            e.CanExecute = true;
        }

        private void ContextMenu_Click(object sender, RoutedEventArgs e)
        {
            var menuItem = ((MenuItem) e.Source);
            var menu = menuItem.Parent as ContextMenu;
            if (!string.IsNullOrEmpty(menuItem.Name) && menu != null)
            {
                switch (menuItem.Name)
                {
                    case "CloseAll":
                        tabControl.Items.Clear();
                        break;
                    case "CloseAllButThis":
                        var tabs = tabControl.Items;
                        var selected = ((TabItem)menu.PlacementTarget).Content as bdUnitPreviewWindow;
                        var count = tabs.Count;
                        var tabsToRemove = new List<TabItem>();
                        for (var i = 0; i < count; i++)
                        {
                            var preview = ((TabItem)tabs[i]).Content as bdUnitPreviewWindow;
                            if (preview.Id != selected.Id)
                            {
                                tabsToRemove.Add(tabs[i] as TabItem);
                            }
                        }
                        tabsToRemove.ForEach(tabs.Remove);
                        break;
                }
            }
            
            
        }
    }
}