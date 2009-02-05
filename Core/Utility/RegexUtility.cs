#region Using Statements

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

        public static bool IsDecimal(string target)
        {
            return Regex.IsMatch(target, "^\\d+(\\.\\d+)$");
        }
    }
}
