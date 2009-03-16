#region Using Statements

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Forms;
using System.Windows.Input;
using bdUnit.Core;
using bdUnit.Core.Enum;
using bdUnit.Preview.Code;
using bdUnit.Preview.Controls;
using ContextMenu=System.Windows.Controls.ContextMenu;
using MenuItem=System.Windows.Controls.MenuItem;
using MessageBox=System.Windows.MessageBox;

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
        }

        #region Properties

        private Parser _parser;
        private UnitTestFrameworkEnum CurrentFramework
        {
            get
            {
                var options = new List<MenuItem> { Menu.NUnit, Menu.XUnit, Menu.MbUnit };
                var selectedOption = options.Find(o => o.IsChecked);
                return (UnitTestFrameworkEnum)Enum.Parse(typeof(UnitTestFrameworkEnum), selectedOption.Name);
            }
        }

        #endregion

        #region Events

        private void Window1_Loaded(object sender, RoutedEventArgs e)
        {
            _parser = new Parser();
            var tab = new TabItem
            {
                Header =
                    new TextBlock
                    {
                        Text = "[Untitled]",
                        TextTrimming = TextTrimming.CharacterEllipsis,
                        TextWrapping = TextWrapping.NoWrap
                    },
                Content = new bdUnitPreviewWindow(_parser),
                MaxWidth = 120,
                MinWidth = 100
            };
            tab.ContextMenu = GenerateContextMenu(tab);
            tabControl.Items.Add(tab);
            tabControl.SelectedIndex = tabControl.Items.Count - 1;
            Closing += Window1_Closing;
            Menu.GenerateDll.Click += GenerateDll_Click;
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
            for (var i = 0; i < tabCount; i++)
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

        void Window1_Closing(object sender, CancelEventArgs e)
        {
            try
            {
                for (var i = 0; i < tabControl.Items.Count; i++)
                {
                    var item = tabControl.Items[i] as TabItem;
                    if (item != null)
                    {
                        var bdUnitPreviewWindow1 = ((bdUnitPreviewWindow)item.Content);
                        bdUnitPreviewWindow1.Dispose();
                    }
                }
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
                    var tab = new TabItem
                                  {
                                      Header =
                                          new TextBlock
                                              {
                                                  Text = "[Untitled]",
                                                  TextTrimming = TextTrimming.CharacterEllipsis,
                                                  TextWrapping = TextWrapping.NoWrap
                                              },
                                      Content = new bdUnitPreviewWindow(_parser),
                                      MaxWidth= 120,
                                      MinWidth= 100
                                  };
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
                            var bdUnitPreview = new bdUnitPreviewWindow(filePaths[i], Menu.CurrentFramework, _parser)
                            {
                                CurrentTabIndex = tabControl.Items.Count,
                                FilePath = filePaths[i],
                                FileName = fileNames[i]
                            };
                            var openTab = new TabItem
                                              {
                                                  Header =
                                                      new TextBlock
                                                          {
                                                              Text = fileNames[i],
                                                              TextTrimming = TextTrimming.CharacterEllipsis,
                                                              TextWrapping = TextWrapping.NoWrap
                                                          },
                                                  Content = bdUnitPreview,
                                                  IsSelected = true,
                                                  MaxWidth = 120,
                                                  MinWidth = 100
                                              };
                            openTab.ContextMenu = GenerateContextMenu(openTab);
                            tabControl.Items.Add(openTab);
                            tabControl.SelectedIndex = tabControl.Items.Count - 1;
                        }
                    }
                    break;
                case "Close":
                    var currentTab = tabControl.SelectedItem;
                    var bdUnit = ((TabItem) currentTab).Content as bdUnitPreviewWindow;
                    if (bdUnit != null) bdUnit.Dispose();
                    tabControl.Items.Remove(currentTab);
                    break;
                case "Save":
                    var preview = ((TabItem)tabControl.SelectedItem).Content as bdUnitPreviewWindow;
                    if (preview != null && !preview.IsSaved)
                    {
                        var range = new TextRange(preview.InputEditor.Document.ContentStart, preview.InputEditor.Document.ContentEnd);
                        var text = range.Text;
                        if (string.IsNullOrEmpty(preview.FilePath))
                        {
                            var saveFileDialog = new SaveFileDialog {Filter = "Input text | *.input", RestoreDirectory = true};
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
                        if (preview.FilePath != null)
                        {
                            var info = new FileInfo(preview.FilePath);
                            var writer = info.CreateText();
                            writer.Write(text);
                            writer.Close();

                            preview.IsSaved = true;
                            var header = ((TabItem)tabControl.SelectedItem).Header as TextBlock;
                            if (header != null)
                            {
                                header.Text = preview.FileName;
                                header.FontWeight = FontWeights.Normal;
                            }
                        }
                    }
                    break;
            }
        }

        private void GenerateDll_Click(object sender, RoutedEventArgs e)
        {
            var dllBuilder = new DllBuilder(_parser);
            var filePaths = new string[] {};
            if (Menu.DllFromOpenDocs.IsChecked)
            {
                filePaths = GetOpenFilePaths();
            }
            if (Menu.DllFromSelectedDocs.IsChecked)
            {
                var openFileDialog = new OpenFileDialog
                                             {
                                                 Multiselect = true,
                                                 Filter = "Input text | *.input",
                                                 RestoreDirectory = true
                                             };
                if (openFileDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                {
                    filePaths = openFileDialog.FileNames;
                }
            }
            var filePath = filePaths[0] ?? filePaths[1];
            var parentFolder = Directory.GetParent(filePath);
            if (parentFolder != null)
            {
                Directory.SetCurrentDirectory(parentFolder.ToString());
                var message = dllBuilder.CompileDll(filePaths, CurrentFramework);
                MessageBox.Show(message);
                if (message.Contains("Successfully"))
                {
                    Process.Start("explorer.exe", parentFolder.ToString());
                }
            }
        }

        private void Command_CanExecute(object sender, CanExecuteRoutedEventArgs e)
        {
            e.CanExecute = true;
        }

        private void ContextMenu_Click(object sender, RoutedEventArgs e)
        {
            var menuItem = ((MenuItem)e.Source);
            var menu = menuItem.Parent as ContextMenu;
            if (!string.IsNullOrEmpty(menuItem.Name) && menu != null)
            {
                switch (menuItem.Name)
                {
                    case "Close":
                        var selectedTab = ((TabItem) menu.PlacementTarget);
                        tabControl.Items.Remove(selectedTab);
                        break;
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

        #endregion Events

        #region Methods

        private string[] GetOpenFilePaths()
        {
            var tabs = tabControl.Items;
            var count = tabs.Count;
            var paths = new string[count];
            for (var i = 0; i < count; i++)
            {
                var tab = (TabItem)tabs[i];
                var bdUnitPreview = tab.Content as bdUnitPreviewWindow;
                if (bdUnitPreview != null) paths[i] = bdUnitPreview.FilePath;
            }
            return paths;
        }

        private ContextMenu GenerateContextMenu(UIElement tab)
        {
            var contextMenu = new ContextMenu { PlacementTarget = tab };
            var close = new MenuItem { Header = "Close", Name = "Close" };
            var closeAll = new MenuItem { Header = "Close All", Name = "CloseAll" };
            var closeAllBut = new MenuItem { Header = "Close All But This", Name = "CloseAllButThis" };
            var menus = new List<MenuItem> { close, closeAll, closeAllBut };
            menus.ForEach(m =>
            {
                m.Click += ContextMenu_Click;
                contextMenu.Items.Add(m);
            });
            return contextMenu;
        }

        #endregion
    }
}