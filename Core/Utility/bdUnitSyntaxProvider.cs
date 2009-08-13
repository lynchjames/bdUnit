#region Using Statements

using System.Collections.Generic;
using System.Windows.Documents;
using System.Windows.Media;

#endregion

namespace bdUnit.Core.Utility
{
    public class bdUnitSyntaxProvider
    {
        private static readonly SolidColorBrush CommentColor = new SolidColorBrush(Colors.ForestGreen);
        private static readonly SolidColorBrush DefaultKeywordColor = new SolidColorBrush(Colors.Orange);
        private static readonly SolidColorBrush MethodColor = new SolidColorBrush(Colors.LightSkyBlue);
        private static readonly SolidColorBrush PropertyColor = new SolidColorBrush(Colors.BlueViolet);
        private static readonly SolidColorBrush SetupColor = new SolidColorBrush(Colors.Red);
        private static readonly List<char> specials = new List<char>();
        private static readonly List<string> tags = new List<string>();
        private static readonly SolidColorBrush TypeColor = new SolidColorBrush(Colors.Yellow);

        static bdUnitSyntaxProvider()
        {
            string[] strs = {
                                "@",
                                "~",
                                "#",
                                "another",
                                "several",
                                "many",
                                "other",
                                "all",
                                "begin",
                                "end",
                                "story",
                                "setup"
                            };
            tags = new List<string>(strs);

            char[] chrs = {
                              '.',
                              ')',
                              '(',
                              '[',
                              ']',
                              '>',
                              '<',
                              ':',
                              ';'
                          };
            specials = new List<char>(chrs);
        }

        public static List<char> GetSpecials
        {
            get { return specials; }
        }

        public static List<string> GetTags
        {
            get { return tags; }
        }

        public static bool IsKnownTag(string tag)
        {
            return tags.Exists(s => tag.ToLower().Contains(s.ToLower()));
        }

        public static List<string> GetJSProvider(string tag)
        {
            return tags.FindAll(s => s.ToLower().StartsWith(tag.ToLower()));
        }

        public static SolidColorBrush GetBrushColor(string tag)
        {
            if (tag.Contains("//") && !tag.Contains("://"))
            {
                return CommentColor;
            }
            if (tag.Contains("@"))
            {
                return TypeColor;
            }
            if (tag.Contains("#"))
            {
                return MethodColor;
            }
            if (tag.Contains("~"))
            {
                return PropertyColor;
            }
            if (tag.Contains("begin") || tag.Contains("end") || tag.Contains("setup") || tag.Contains("story"))
            {
                return SetupColor;
            }
            return DefaultKeywordColor;
        }

        #region Nested type: Tag

        public struct Tag
        {
            public TextPointer EndPosition;
            public TextPointer StartPosition;
            public string Word;
        }

        #endregion
    }
}