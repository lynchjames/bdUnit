using System;
using System.Collections.Generic;
using System.Text;
using System.Windows;
using System.Windows.Forms.Integration;
using System.Windows.Input;
using bdUnit.Core;
using Core.Enum;
using ScintillaNet;
using TextRange=System.Windows.Documents.TextRange;

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
        }

        private UnitTestFrameworkEnum CurrentFramework { get; set; }

        private void Window1_Loaded(object sender, RoutedEventArgs e)
        {
            LoadEditor();
            Editor.KeyDown += Editor_KeyDown;
            Paste.Click += Paste_Click;
            XUnitPreview.Click += XUnitPreview_Click;
            NUnitPreview.Click += NUnitPreview_Click;
            MbUnitPreview.Click += MbUnitPreview_Click;
            Editor.Document.TextAlignment = TextAlignment.Justify;
        }

        private void MbUnitPreview_Click(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.MbUnit;
            UpdatePreview(CurrentFramework);
            Title = "BDUnit Preview - " + UnitTestFrameworkEnum.MbUnit;
        }

        private void NUnitPreview_Click(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.NUnit;
            UpdatePreview(CurrentFramework);
            Title = "BDUnit Preview - " + UnitTestFrameworkEnum.NUnit;
        }

        private void XUnitPreview_Click(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.XUnit;
            UpdatePreview(CurrentFramework);
            Title = "BDUnit Preview - " + UnitTestFrameworkEnum.XUnit;
        }

        private void Paste_Click(object sender, RoutedEventArgs e)
        {
            Editor.Paste();
        }

        private void LoadEditor()
        {
            //Editor.Document.Foreground = new SolidColorBrush(Colors.White);
            //Editor.Background = new SolidColorBrush(Colors.Black);
            var editor = new Scintilla {Name = "sciEditor", AcceptsReturn = true, AcceptsTab = true};
            editor.Encoding = Encoding.UTF8;
            editor.ConfigurationManager.Language = "cs";
            editor.LineWrap.Mode = WrapMode.None;
            
            //editor.Styles[editor.Lexing.StyleNameMap["OPERATOR"]].ForeColor = Color.Brown;
            //editor.Styles[editor.Lexing.StyleNameMap["GLOBALCLASS"]].ForeColor = Color.Yellow;
            //editor.Styles[editor.Lexing.StyleNameMap["IDENTIFIER"]].ForeColor = Color.Yellow;
            //editor.Styles.Default.BackColor = Color.Black;
            //editor.ForeColor = Color.Black;
            //editor.Caret.Color = Color.White;

            var host = new WindowsFormsHost {Child = editor};
            Preview.Content = host;
        }

        private void Editor_KeyDown(object sender, KeyEventArgs e)
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
            var paths = new Dictionary<string, string> {{"grammar", "../../../Core//Grammar/TestWrapper.mg"}};
            var textRange = new TextRange(Editor.Document.ContentStart, Editor.Document.ContentEnd);
            if (!textRange.IsEmpty)
            {
                var parser = new Parser(textRange.Text, paths);
                var host = Preview.Content as WindowsFormsHost;
                var sciEditor = host.Child as Scintilla;
                if (sciEditor != null)
                {
                    sciEditor.ResetText();
                    sciEditor.InsertText(0, parser.Preview(framework));
                }
            }
        }
    }
}