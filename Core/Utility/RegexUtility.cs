#region Using Statements

using System;
using System.Text.RegularExpressions;

#endregion

namespace bdUnit.Core.Utility
{
    public class RegexUtility
    {
        public static bool IsString(string target)
        {
            return Regex.IsMatch(target, "[A-Z]|[a-z]");
        }

        public static bool IsInteger(string target)
        {
            return Regex.IsMatch(target, "0|0*[1-9][0-9]*");
        }

        public static bool IsDouble(string target)
        {
            return Regex.IsMatch(target, "^\\d+(\\.\\d+)$");
        }

        public static bool IsDateTime(string target)
        {
            return Regex.IsMatch(target, "(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\\d\\d");
        }

        public static bool IsBool(string target)
        {
            bool isBool;
            return Boolean.TryParse(target, out isBool);
        }
    }
}
