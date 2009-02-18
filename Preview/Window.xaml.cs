#region Using Statements

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Documents;
using System.Windows.Forms.Integration;
using System.Windows.Input;
using bdUnit.Core;
using Core.Enum;
using Microsoft.Win32;
using ScintillaNet;
using TextRange=System.Windows.Documents.TextRange;

#endregion

namespace Preview
{
    /// <summary>
    /// Interaction logic for Window1.xaml
    /// </summary>
    public partial class Window1
    {
        private string SelectedDirectory { get; set; }

        public Window1()
        {
            InitializeComponent();
            Loaded += Window1_Loaded;
        }

        private UnitTestFrameworkEnum CurrentFramework { get; set; }

        private void Window1_Loaded(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.NUnit;
            LoadEditor();
            InputEditor.KeyDown += InputEditor_KeyDown;
            SelectFolder.Click += SelectFolder_Click;
            Paste.Click += Paste_Click;
            Dll.Click += Dll_Click;
            XUnitPreview.Click += XUnitPreview_Click;
            NUnitPreview.Click += NUnitPreview_Click;
            MbUnitPreview.Click += MbUnitPreview_Click;
            var range = new TextRange(InputEditor.Document.ContentStart, InputEditor.Document.ContentEnd);
            var defaultText = File.ReadAllText("../../../Core/Inputs/LogansRun.input");
            Debug.Write(defaultText);
            range.Text = defaultText;
            InputEditor.Document.TextAlignment = TextAlignment.Justify;
            InputEditor.Document.LineHeight = 5;
        }

        void SelectFolder_Click(object sender, RoutedEventArgs e)
        {
            var folderDialog = new System.Windows.Forms.FolderBrowserDialog();
            folderDialog.ShowDialog();
            SelectedDirectory = folderDialog.SelectedPath;
            // Add code to load up inputs in tabs within the preview windows
        }

        void Dll_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(SelectedDirectory))
            {
                var dllBuilder = new DllBuilder();
                MessageBox.Show(dllBuilder.CompileDll(SelectedDirectory, CurrentFramework));
            }
            else
            {
               MessageBox.Show("Please select a folder", "bdUnit - No Inputs Selected", MessageBoxButton.OK, MessageBoxImage.Exclamation);
            }
        }

        private void MbUnitPreview_Click(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.MbUnit;
            UpdatePreview(CurrentFramework);
            Title = "bdUnit Preview - " + UnitTestFrameworkEnum.MbUnit;
        }

        private void NUnitPreview_Click(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.NUnit;
            UpdatePreview(CurrentFramework);
            Title = "bdUnit Preview - " + UnitTestFrameworkEnum.NUnit;
        }

        private void XUnitPreview_Click(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.XUnit;
            UpdatePreview(CurrentFramework);
            Title = "bdUnit Preview - " + UnitTestFrameworkEnum.XUnit;
        }

        private void Paste_Click(object sender, RoutedEventArgs e)
        {
            InputEditor.Paste();
        }

        private void LoadEditor()
        {
            //InputEditor.Document.Foreground = new SolidColorBrush(Colors.White);
            //InputEditor.Background = new SolidColorBrush(Colors.Black);
            var sciEditor = new Scintilla {Name = "sciEditor", AcceptsReturn = true, AcceptsTab = true};
            sciEditor.Encoding = Encoding.UTF8;
            sciEditor.ConfigurationManager.Language = "cs";
            sciEditor.LineWrap.Mode = WrapMode.None;
            
            //editor.Styles[editor.Lexing.StyleNameMap["OPERATOR"]].ForeColor = Color.Brown;
            //editor.Styles[editor.Lexing.StyleNameMap["GLOBALCLASS"]].ForeColor = Color.Yellow;
            //editor.Styles[editor.Lexing.StyleNameMap["IDENTIFIER"]].ForeColor = Color.Yellow;
            //editor.Styles.Default.BackColor = Color.Black;
            //editor.ForeColor = Color.Black;
            //editor.Caret.Color = Color.White;

            var host = new WindowsFormsHost {Child = sciEditor};
            Preview.Content = host;
        }

        private void InputEditor_KeyDown(object sender, KeyEventArgs e)
        {
            var host = Preview.Content as WindowsFormsHost;
            var sciEditor = host.Child as Scintilla;
            if (e.Key == Key.F5 || e.Key == Key.OemPeriod || e.Key == Key.Return || e.Key == Key.Enter)
            {
                UpdatePreview(CurrentFramework);
            }
            else if (sciEditor != null)
            {
                sciEditor.ResetText();
                sciEditor.InsertText(0, "Input has been modified, hit F5 to refresh");
            }
        }

        private void UpdatePreview(UnitTestFrameworkEnum framework)
        {
            var paths = new Dictionary<string, string> {{"grammar", Settings.GrammarPath}};
            var textRange = new TextRange(InputEditor.Document.ContentStart, InputEditor.Document.ContentEnd);
            if (!textRange.IsEmpty)
            {
                var parser = new Parser(textRange.Text, paths);
                var host = Preview.Content as WindowsFormsHost;
                var sciEditor = host.Child as Scintilla;
                if (sciEditor != null)
                {
                    sciEditor.ResetText();
                    sciEditor.InsertText(0, parser.Parse(framework));

                    //TODO Modify input text if parsing exception is raised
                    TextPointer point = InputEditor.Document.ContentStart;
                }
            }
        }
    }
}