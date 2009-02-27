﻿using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Forms.Integration;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Windows.Threading;
using bdUnit.Core;
using bdUnit.Core.Utility;
using Core.Enum;
using ScintillaNet;
using TextRange=System.Windows.Documents.TextRange;

namespace bdUnit.Preview.Controls
{
    /// <summary>
    /// Interaction logic for bdUnitPreviewWindow.xaml
    /// </summary>
    public partial class bdUnitPreviewWindow : UserControl
    {
        public bdUnitPreviewWindow()
        {
            InitializeComponent();
            Loaded += bdPreviewWindow_Loaded;
        }

        private string SelectedDirectory { get; set; }
        private TextPointer ErrorPoint { get; set; }
        private double ErrorVerticalOffset { get; set; }
        private bool BackgroundThreadIsRunning { get; set; }
        private DateTime LastUpdated { get; set; }
        private UnitTestFrameworkEnum CurrentFramework { get; set; }
        private System.Timers.Timer _timer;

        [STAThread]
        private void bdPreviewWindow_Loaded(object sender, RoutedEventArgs e)
        {
            _timer = new System.Timers.Timer();
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
            range.Text = defaultText;
            InputEditor.TextChanged += InputEditor_TextChanged;
            InputEditor.Document.TextAlignment = TextAlignment.Justify;
            InputEditor.Document.LineHeight = 5;
            ErrorOutput.MouseLeftButtonDown += ErrorOutput_MouseLeftButtonDown;
            ErrorOutput.MouseEnter += ErrorOutput_MouseEnter;
            ErrorOutput.MouseLeave += ErrorOutput_MouseLeave;
            ErrorVerticalOffset = -1;
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
            _timer.Stop();
            _timer.Interval = 300;
            _timer.Elapsed += _timer_Elapsed;
            _timer.Start();
        }

        void _timer_Elapsed(object sender, System.Timers.ElapsedEventArgs e)
        {
            _timer.Elapsed -= _timer_Elapsed;
            if (!BackgroundThreadIsRunning && !IsUpdating)
            {
                BackgroundThreadIsRunning = true;
                var BackgroundThreadStart = new ThreadStart(UpdatePreview);
                var BackgroundThread = new Thread(BackgroundThreadStart);
                BackgroundThread.Name = "Update Preview";
                BackgroundThread.IsBackground = true;
                BackgroundThread.Start();
            }
        }

        private void HighlightInputSyntax()
        {
            if (InputEditor.Document == null)
                return;
            IsUpdating = true;
            if (!InputEditor.Dispatcher.CheckAccess())
            {
                InputEditor.Dispatcher.Invoke(DispatcherPriority.SystemIdle, new Action(Highlight));
            }
            else
            {
                Highlight();
            }
            IsUpdating = false;
        }

        private void Highlight()
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

        List<bdUnitSyntaxProvider.Tag> m_tags = new List<bdUnitSyntaxProvider.Tag>();
        private bool IsUpdating;

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
                InputEditor.Dispatcher.Invoke(DispatcherPriority.SystemIdle, new Action(Update));
            }
            else
            {
                Update();
            }
            BackgroundThreadIsRunning = false;
            LastUpdated = DateTime.Now;
        }

        private void Update()
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
                    if (errorStartPoint != null)
                    {
                        var errorEndPoint = errorStartPoint.GetPositionAtOffset(ex.Location.Span.Length + 4);
                        if (errorEndPoint != null)
                        {
                            var errorRange = new TextRange(errorStartPoint, errorEndPoint);
                            errorRange.ApplyPropertyValue(TextElement.BackgroundProperty, Brushes.DimGray);
                            ErrorPoint = errorEndPoint;
                            ErrorVerticalOffset = ex.Location.Span.Start.Line - 1; 
                        }
                    }
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
            //TODO Move this to window
            //Title = "bdUnit Preview - " + framework;
        }
    }
}