using System.Collections.Generic;
using System.Windows.Documents;
using System.Windows.Media;

namespace bdUnit.Core.Utility
{
    public class bdUnitSyntaxProvider
    {
        static List<string> tags = new List<string>();
        static List<char> specials = new List<char>();

        public struct Tag
        {
            public TextPointer StartPosition;
            public TextPointer EndPosition;
            public string Word;
        }

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

        private static readonly SolidColorBrush TypeColor = new SolidColorBrush(Colors.Yellow);
        private static readonly SolidColorBrush PropertyColor = new SolidColorBrush(Colors.PaleVioletRed);
        private static readonly SolidColorBrush MethodColor = new SolidColorBrush(Colors.BlueViolet);
        private static readonly SolidColorBrush SetupColor = new SolidColorBrush(Colors.Red);
        private static readonly SolidColorBrush DefaultKeywordColor = new SolidColorBrush(Colors.Orange);

        public static SolidColorBrush GetBrushColor(string tag)
        {
            if (tag.Contains("@"))
            {
                return TypeColor;
            }
            else if (tag.Contains("#"))
            {
                return MethodColor;
            }
            else if (tag.Contains("~"))
            {
                return PropertyColor;
            }
            else if (tag.Contains("begin") || tag.Contains("end") || tag.Contains("setup") || tag.Contains("story"))
            {
                return SetupColor;
            }
            return DefaultKeywordColor;
        }
    }
}
