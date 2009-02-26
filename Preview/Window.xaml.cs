﻿#region Using Statements

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
using System.Windows.Threading;
using bdUnit.Core;
using bdUnit.Core.Utility;
using Core.Enum;
using ScintillaNet;
using Brushes=System.Windows.Media.Brushes;
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
        private TextPointer ErrorPoint { get; set; }
        private double ErrorVerticalOffset { get; set; }
        private bool BackgroundThreadIsRunning { get; set; }
        private DateTime LastUpdated { get; set; }

        public Window1()
        {
            InitializeComponent();
            Loaded += Window1_Loaded;
        }

        private UnitTestFrameworkEnum CurrentFramework { get; set; }

        [STAThread]
        private void Window1_Loaded(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.NUnit;
            LoadEditor();
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
            InputEditor.TextChanged += InputEditor_TextChanged;
            InputEditor.Document.TextAlignment = TextAlignment.Justify;
            InputEditor.Document.LineHeight = 5;
            ErrorOutput.MouseLeftButtonDown += ErrorOutput_MouseLeftButtonDown;
            ErrorOutput.MouseEnter += ErrorOutput_MouseEnter;
            ErrorOutput.MouseLeave += ErrorOutput_MouseLeave;
            ErrorVerticalOffset = -1;
            Closed += Window1_Closed;
            HighlightInputSyntax();
        }

        void ErrorOutput_MouseLeave(object sender, MouseEventArgs e)
        {
            if (ErrorVerticalOffset != -1)
            {
                ErrorOutput.FontWeight = FontWeights.Normal;
                ErrorOutput.FontStyle = FontStyles.Normal;
            }
        }

        void ErrorOutput_MouseEnter(object sender, MouseEventArgs e)
        {
            if (ErrorVerticalOffset != -1)
            {
                ErrorOutput.FontWeight = FontWeights.Bold;
                ErrorOutput.FontStyle = FontStyles.Italic;
            }
        }

        void ErrorOutput_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (ErrorVerticalOffset != -1)
            {
                InputEditor.ScrollToVerticalOffset(ErrorVerticalOffset);
                InputEditor.CaretPosition = ErrorPoint;
            }
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
            UpdatePreview();
        }

        private void NUnitPreview_Click(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.NUnit;
            UpdatePreview();
        }

        private void XUnitPreview_Click(object sender, RoutedEventArgs e)
        {
            CurrentFramework = UnitTestFrameworkEnum.XUnit;
            UpdatePreview();
        }

        private void Paste_Click(object sender, RoutedEventArgs e)
        {
            InputEditor.Paste();
        }

        private void LoadEditor()
        {
            InputEditor.Document.Foreground = new SolidColorBrush(Colors.White);
            InputEditor.Background = new SolidColorBrush(Colors.Black);
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

        private void InputEditor_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (!BackgroundThreadIsRunning)
            {
                BackgroundThreadIsRunning = true;
                var BackgroundThreadStart = new ThreadStart(UpdatePreview);
                var BackgroundThread = new Thread(BackgroundThreadStart);
                BackgroundThread.Name = "Update Preview";
                BackgroundThread.IsBackground = true;
                BackgroundThread.Start();
            }
            //var textRange = new TextRange(InputEditor.Document.ContentStart, InputEditor.Document.ContentEnd);
            //textRange.ApplyPropertyValue(TextElement.BackgroundProperty, Brushes.Black);
            //var host = Preview.Content as WindowsFormsHost;
            //var sciEditor = host.Child as Scintilla;
            //if (e.Key == Key.F5 || e.Key == Key.OemPeriod || e.Key == Key.Return || e.Key == Key.Enter)
            //{
            //if (!BackgroundThreadIsRunning)
            //{
            //    var BackgroundThreadStart = new ThreadStart(UpdatePreview);
            //    var BackgroundThread = new Thread(BackgroundThreadStart);
            //    BackgroundThread.Name = "Update Preview";
            //    BackgroundThread.IsBackground = true;
            //    BackgroundThread.
            //    BackgroundThread.Start();
            //    BackgroundThreadIsRunning = true;
            //}
            //}
            //if (sciEditor != null)
            //{
            //    sciEditor.ResetText();
            //    sciEditor.InsertText(0, "Input has been modified, hit F5 to refresh");
            //}
        }

        private void HighlightInputSyntax()
        {
            if (InputEditor.Document == null)
                return;

            if (!InputEditor.Dispatcher.CheckAccess())
            {
                InputEditor.Dispatcher.Invoke(DispatcherPriority.SystemIdle, new Action(
            delegate()
                {
                    TextRange documentRange = new TextRange(InputEditor.Document.ContentStart,
                                                            InputEditor.Document.ContentEnd);
                    documentRange.ClearAllProperties();

                    TextPointer navigator = InputEditor.Document.ContentStart;
                    while (navigator.CompareTo(InputEditor.Document.ContentEnd) < 0)
                    {
                        TextPointerContext context = navigator.GetPointerContext(LogicalDirection.Backward);
                        if (context == TextPointerContext.ElementStart && navigator.Parent is Run)
                        {
                            CheckWordsInRun((Run) navigator.Parent);
                        }
                        navigator = navigator.GetNextContextPosition(LogicalDirection.Forward);
                    }
                    Format();
                }
                                                                                                          ));
            }
            else
            {
                TextRange documentRange = new TextRange(InputEditor.Document.ContentStart, InputEditor.Document.ContentEnd);
                documentRange.ClearAllProperties();

                TextPointer navigator = InputEditor.Document.ContentStart;
                while (navigator.CompareTo(InputEditor.Document.ContentEnd) < 0)
                {
                    TextPointerContext context = navigator.GetPointerContext(LogicalDirection.Backward);
                    if (context == TextPointerContext.ElementStart && navigator.Parent is Run)
                    {
                        CheckWordsInRun((Run)navigator.Parent);
                    }
                    navigator = navigator.GetNextContextPosition(LogicalDirection.Forward);
                }
                Format();
            }
        }

        List<bdUnitSyntaxProvider.Tag> m_tags = new List<bdUnitSyntaxProvider.Tag>();
        void Format()
        {
            for(var i = 0; i< m_tags.Count; i++)
            {
                var range = new TextRange(m_tags[i].StartPosition, m_tags[i].EndPosition);
                var syntaxColor = bdUnitSyntaxProvider.GetBrushColor(m_tags[i].Word);
                range.ApplyPropertyValue(TextElement.ForegroundProperty, syntaxColor);
                range.ApplyPropertyValue(TextElement.FontWeightProperty, FontWeights.Bold);
            }
            m_tags.Clear();
        }

        void CheckWordsInRun(Run run)
        {
            string text = run.Text;

            int sIndex = 0;
            int eIndex = 0;
            for (int i = 0; i < text.Length; i++)
            {
                if (Char.IsWhiteSpace(text[i]) | bdUnitSyntaxProvider.GetSpecials.Contains(text[i]))
                {
                    if (i > 0 && !(Char.IsWhiteSpace(text[i - 1]) | bdUnitSyntaxProvider.GetSpecials.Contains(text[i - 1])))
                    {
                        eIndex = i - 1;
                        string word = text.Substring(sIndex, eIndex - sIndex + 1);

                        if (bdUnitSyntaxProvider.IsKnownTag(word))
                        {
                            bdUnitSyntaxProvider.Tag t = new bdUnitSyntaxProvider.Tag();
                            t.StartPosition = run.ContentStart.GetPositionAtOffset(sIndex, LogicalDirection.Forward);
                            t.EndPosition = run.ContentStart.GetPositionAtOffset(eIndex + 1, LogicalDirection.Backward);
                            t.Word = word;
                            m_tags.Add(t);
                        }
                    }
                    sIndex = i + 1;
                }
            }

            string lastWord = text.Substring(sIndex, text.Length - sIndex);
            if (bdUnitSyntaxProvider.IsKnownTag(lastWord))
            {
                bdUnitSyntaxProvider.Tag t = new bdUnitSyntaxProvider.Tag();
                t.StartPosition = run.ContentStart.GetPositionAtOffset(sIndex, LogicalDirection.Forward);
                t.EndPosition = run.ContentStart.GetPositionAtOffset(eIndex + lastWord.Length + 2, LogicalDirection.Backward);
                t.Word = lastWord;
                m_tags.Add(t);
            }
        }

        private void UpdatePreview()
        {
            if (!InputEditor.Dispatcher.CheckAccess())
            {
                InputEditor.Dispatcher.Invoke(DispatcherPriority.SystemIdle, new Action(
            delegate()
            {
                var framework = CurrentFramework;
                var paths = new Dictionary<string, string> { { "grammar", Settings.GrammarPath } };
                var textRange = new TextRange(InputEditor.Document.ContentStart, InputEditor.Document.ContentEnd);
                if (!textRange.IsEmpty)
                {
                    var outputCode = string.Empty;
                    var error = string.Empty;
                    try





















                    {
                        HighlightInputSyntax();
                        var parser = new Parser(textRange.Text, paths);
                        outputCode = parser.Parse(framework);
                    }
                    catch (DynamicParserExtensions.ErrorException ex)
                    {
                        //TODO Modify input text if parsing exception is raised
                        var errorStartPoint =
                            textRange.Start.GetLineStartPosition(ex.Location.Span.Start.Line - 1).
                                GetPositionAtOffset(ex.Location.Span.Start.Column);
                        var errorEndPoint = errorStartPoint.GetPositionAtOffset(ex.Location.Span.Length + 4);
                        var errorRange = new TextRange(errorStartPoint, errorEndPoint);
                        errorRange.ApplyPropertyValue(TextElement.BackgroundProperty, Brushes.Red);
                        ErrorPoint = errorEndPoint;
                        ErrorVerticalOffset = ex.Location.Span.Start.Line - 1;
                        error = ex.Message;
                        ErrorOutput.Cursor = Cursors.Hand;
                    }
                    finally
                    {
                        var host = Preview.Content as WindowsFormsHost;
                        var sciEditor = host.Child as Scintilla;
                        if (sciEditor != null)
                        {
                            sciEditor.ResetText();
                            sciEditor.InsertText(0, outputCode);
                            ErrorOutput.Text = error;
                        }
                    }
                }
                CurrentFramework = framework;
                Title = "bdUnit Preview - " + framework;
            }));
            }
            //Thread.Sleep(10000);
            BackgroundThreadIsRunning = false;
        }

        void Window1_Closed(object sender, System.EventArgs e)
        {
            try
            {
                var host = (WindowsFormsHost)Preview.Content;
                host.Dispose();
            }
            catch (Exception)
            {

            }
        }
    }
}
