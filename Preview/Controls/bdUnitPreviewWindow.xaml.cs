﻿#region Using Statements

using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Text;
using System.Threading;
using System.Timers;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Forms;
using System.Windows.Forms.Integration;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using bdUnit.Core;
using bdUnit.Core.Enum;
using bdUnit.Core.Utility;
using bdUnit.Preview.Code;
using ScintillaNet;
using Brushes=System.Windows.Media.Brushes;
using Cursors=System.Windows.Input.Cursors;
using KeyEventArgs=System.Windows.Input.KeyEventArgs;
using MouseEventArgs=System.Windows.Input.MouseEventArgs;
using TextRange=System.Windows.Documents.TextRange;
using Timer=System.Timers.Timer;

#endregion

namespace bdUnit.Preview.Controls
{
    /// <summary>
    /// Interaction logic for bdUnitPreviewWindow.xaml
    /// </summary>
    public partial class bdUnitPreviewWindow : IDisposable
    {
        #region Constructor

        public bdUnitPreviewWindow()
        {
            InitializeComponent();
            Id = Guid.NewGuid();
            Loaded += bdPreviewWindow_Loaded;
            Load();
        }

        public bdUnitPreviewWindow(Parser parser)
        {
            InitializeComponent();
            _parser = parser;
            Id = Guid.NewGuid();
            Loaded += bdPreviewWindow_Loaded;
            Load();
        }

        public bdUnitPreviewWindow(string filePath, UnitTestFrameworkEnum framework, Parser parser)
        {
            InitializeComponent();
            _parser = parser;
            _parser = parser;
            Id = Guid.NewGuid();
            Loaded += bdPreviewWindow_Loaded;
            var range = new TextRange(InputEditor.Document.ContentStart, InputEditor.Document.ContentEnd);
            var text = File.ReadAllText(filePath);
            range.Text = text;

            CurrentFramework = framework;
            IsSaved = true;
            Load();
            UpdatePreview();
        }

        #endregion

        #region Properties

        private readonly List<bdUnitSyntaxProvider.Tag> m_tags = new List<bdUnitSyntaxProvider.Tag>();
        public Parser _parser;
        private Timer _timer;
        public string FileName;
        public Guid Id;
        public bool IsSaved;
        private bool IsUpdating;
        private TextPointer ErrorPoint { get; set; }
        private double ErrorVerticalOffset { get; set; }
        private bool BackgroundThreadIsRunning { get; set; }
        private DateTime LastUpdated { get; set; }
        private UnitTestFrameworkEnum CurrentFramework { get; set; }
        public int CurrentTabIndex { get; set; }
        public string FilePath { get; set; }

        private static Scintilla ScintillaEditor
        {
            get
            {
                var sciEditor = new Scintilla
                                    {
                                        Name = "sciEditor",
                                        AcceptsReturn = true,
                                        AcceptsTab = true,
                                        Encoding = Encoding.UTF8,
                                        ConfigurationManager = {Language = "cs"},
                                        LineWrap = {Mode = WrapMode.None}
                                    };
                return sciEditor;
            }
        }

        #endregion

        #region Events

        [STAThread]
        private void bdPreviewWindow_Loaded(object sender, RoutedEventArgs e)
        {
            InputEditor.TextChanged += InputEditor_TextChanged;
            InputEditor.KeyDown += InputEditor_KeyDown;
            ErrorOutput.MouseLeftButtonDown += ErrorOutput_MouseLeftButtonDown;
            ErrorOutput.MouseEnter += ErrorOutput_MouseEnter;
            ErrorOutput.MouseLeave += ErrorOutput_MouseLeave;
            EventBus.FrameworkChecked += EventBus_FrameworkChecked;
        }

        private void EventBus_FrameworkChecked(object sender, EventArgs e)
        {
            var menu = (MenuToolbar) sender;
            if (menu != null)
            {
                CurrentFramework = menu.CurrentFramework;
            }
        }

        private void ErrorOutput_MouseLeave(object sender, MouseEventArgs e)
        {
            if (ErrorVerticalOffset != -1)
            {
                ErrorOutput.FontWeight = FontWeights.Normal;
                ErrorOutput.FontStyle = FontStyles.Normal;
            }
        }

        private void ErrorOutput_MouseEnter(object sender, MouseEventArgs e)
        {
            if (ErrorVerticalOffset != -1)
            {
                ErrorOutput.FontWeight = FontWeights.Bold;
                ErrorOutput.FontStyle = FontStyles.Italic;
            }
        }

        private void ErrorOutput_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (ErrorVerticalOffset != -1)
            {
                InputEditor.ScrollToVerticalOffset(ErrorVerticalOffset);
                InputEditor.CaretPosition = ErrorPoint;
            }
        }

        public void InputEditor_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.F5)
            {
                Update();
            }
        }

        public void InputEditor_TextChanged(object sender, TextChangedEventArgs e)
        {
            IsSaved = false;
            EventBus.TextChanged(this, new TargetEventArgs {TargetId = Id});
            _timer.Stop();
            _timer.Interval = 400;
            _timer.Elapsed += _timer_Elapsed;
            _timer.Start();
        }

        private void _timer_Elapsed(object sender, ElapsedEventArgs e)
        {
            _timer.Stop();
            _timer.Elapsed -= _timer_Elapsed;
            InputEditor.TextChanged -= InputEditor_TextChanged;

            if (!BackgroundThreadIsRunning && !IsUpdating)
            {
                BackgroundThreadIsRunning = true;
                var BackgroundThreadStart = new ThreadStart(UpdatePreview);
                var BackgroundThread = new Thread(BackgroundThreadStart) {Name = "Update Preview", IsBackground = true};
                BackgroundThread.Start();
            }
        }

        #endregion

        #region Methods

        private void Load()
        {
            LoadEditor();
            _timer = new Timer();
            InputEditor.Document.TextAlignment = TextAlignment.Justify;
            InputEditor.Document.LineHeight = 5;
            ErrorVerticalOffset = -1;
        }

        private void LoadEditor()
        {
            InputEditor.Document.Foreground = new SolidColorBrush(Colors.White);
            InputEditor.Background = new SolidColorBrush(Colors.Black);
            var host = new WindowsFormsHost {Child = ScintillaEditor};
            Preview.Content = host;
        }

        private void HighlightInputSyntax()
        {
            if (InputEditor.Document == null)
                return;
            IsUpdating = true;
            if (InputEditor.Dispatcher.CheckAccess())
            {
                InputEditor.Dispatcher.Invoke(DispatcherPriority.Background, new Action(Highlight));
            }
            else
            {
                Highlight();
            }
            IsUpdating = false;
        }

        private void Highlight()
        {
            InputEditor.Background = Brushes.Black;
            var existingRange = new TextRange(InputEditor.Document.ContentStart, InputEditor.Document.ContentEnd);
            existingRange.ClearAllProperties();
            var navigator = InputEditor.Document.ContentStart;
            while (navigator.CompareTo(InputEditor.Document.ContentEnd) < 0)
            {
                var context = navigator.GetPointerContext(LogicalDirection.Backward);
                if (context == TextPointerContext.ElementStart && navigator.Parent is Run)
                {
                    CheckWordsInRun((Run) navigator.Parent);
                }
                navigator = navigator.GetNextContextPosition(LogicalDirection.Forward);
            }
            Format();
        }

        private void Format()
        {
            for (var i = 0; i < m_tags.Count; i++)
            {
                var range = new TextRange(m_tags[i].StartPosition, m_tags[i].EndPosition);
                var syntaxColor = bdUnitSyntaxProvider.GetBrushColor(m_tags[i].Word);
                range.ApplyPropertyValue(TextElement.ForegroundProperty, syntaxColor);
                range.ApplyPropertyValue(TextElement.FontWeightProperty, FontWeights.Bold);
            }
            m_tags.Clear();
        }

        private void CheckWordsInRun(Run run)
        {
            var text = run.Text;

            var sIndex = 0;
            var eIndex = 0;
            for (var i = 0; i < text.Length; i++)
            {
                if (Char.IsWhiteSpace(text[i]) | bdUnitSyntaxProvider.GetSpecials.Contains(text[i]))
                {
                    if (i > 0 &&
                        !(Char.IsWhiteSpace(text[i - 1]) | bdUnitSyntaxProvider.GetSpecials.Contains(text[i - 1])))
                    {
                        if (text.Contains("//") && !text.Contains("://"))
                        {
                            var t = new bdUnitSyntaxProvider.Tag();
                            t.StartPosition = run.ContentStart;
                            t.EndPosition = run.ContentEnd;
                            t.Word = text;
                            m_tags.Add(t);
                        }
                        eIndex = i - 1;
                        var word = text.Substring(sIndex, eIndex - sIndex + 1);

                        if (bdUnitSyntaxProvider.IsKnownTag(word))
                        {
                            var t = new bdUnitSyntaxProvider.Tag();
                            t.StartPosition = run.ContentStart.GetPositionAtOffset(sIndex, LogicalDirection.Forward);
                            t.EndPosition = run.ContentStart.GetPositionAtOffset(eIndex + 1, LogicalDirection.Backward);
                            t.Word = word;
                            m_tags.Add(t);
                        }
                    }
                    sIndex = i + 1;
                }
            }

            var lastWord = text.Substring(sIndex, text.Length - sIndex);
            if (bdUnitSyntaxProvider.IsKnownTag(lastWord))
            {
                var t = new bdUnitSyntaxProvider.Tag();
                t.StartPosition = run.ContentStart.GetPositionAtOffset(sIndex, LogicalDirection.Forward);
                t.EndPosition = run.ContentStart.GetPositionAtOffset(eIndex + lastWord.Length + 2,
                                                                     LogicalDirection.Backward);
                t.Word = lastWord;
                m_tags.Add(t);
            }
        }

        public void UpdatePreview()
        {
            if (!InputEditor.Dispatcher.CheckAccess())
            {
                InputEditor.Dispatcher.Invoke(DispatcherPriority.Background, new Action(HighlightInputSyntax));
            }
            else
            {
                HighlightInputSyntax();
            }
            BackgroundThreadIsRunning = false;
            LastUpdated = DateTime.Now;
            InputEditor.TextChanged += InputEditor_TextChanged;
        }

        private void Update()
        {
            var framework = CurrentFramework;
            var textRange = new TextRange(InputEditor.Document.ContentStart, InputEditor.Document.ContentEnd);
            textRange.ApplyPropertyValue(TextElement.BackgroundProperty, Brushes.Black);
            if (!textRange.IsEmpty)
            {
                var parser = _parser ?? new Parser();
                parser.Input = textRange.Text;
                var outputCode = string.Empty;
                var error = string.Empty;
                try
                {
                    outputCode = parser.Parse(framework);
                }
                catch (DynamicParserExtensions.ParserErrorException ex)
                {
                    var errorStartLine =
                        textRange.Start.GetLineStartPosition(ex.Location.Span.Start.Line - 1);
                    if (errorStartLine != null)
                    {
                        var errorStartPoint = errorStartLine.GetPositionAtOffset(ex.Location.Span.Start.Column);
                        if (errorStartPoint != null)
                        {
                            var errorEndPoint = errorStartPoint.GetPositionAtOffset(ex.Location.Span.Length);
                            if (errorEndPoint != null)
                            {
                                var errorRange = new TextRange(errorStartPoint, errorEndPoint);
                                errorRange.ApplyPropertyValue(TextElement.BackgroundProperty, Brushes.DimGray);
                                ErrorPoint = errorEndPoint;
                                ErrorVerticalOffset = (ex.Location.Span.Start.Line + 5)*InputEditor.Document.LineHeight;
                            }
                        }
                    }
                    error = ex.Message;
                    ErrorOutput.Cursor = Cursors.Hand;
                }
                finally
                {
                    var host = (Preview.Content as WindowsFormsHost) ??
                                            new WindowsFormsHost {Child = ScintillaEditor};
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
        }

        public void ChangeFont()
        {
            var fontDialog = new FontDialog {FontMustExist = true};
            if (fontDialog.ShowDialog(this.Parent as IWin32Window) != DialogResult.None)
            {
                var host = (Preview.Content as WindowsFormsHost) ??
                                            new WindowsFormsHost { Child = ScintillaEditor };
                var sciEditor = host.Child as Scintilla;
                sciEditor.Font = fontDialog.Font;
                sciEditor.Refresh();
            } 
        }

        #endregion

        #region Implementation of IDisposable

        public void Dispose()
        {
            try
            {
                Preview = null;
                InputEditor = null;
            }
            catch (Exception)
            {
            }
        }

        #endregion
    }
}