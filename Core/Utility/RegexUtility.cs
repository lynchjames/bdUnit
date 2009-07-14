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
            //return Regex.IsMatch(target, "(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](17|18|19|20)\\d\\d");
            return Regex.IsMatch(target, @"^(?ni:(((?:((((((?<month>(?<monthname>(Jan(uary)?|Ma(r(ch)?|y)|Jul(y)?|Aug(ust)?|Oct(ober)?|Dec(ember)?)))\ )|(?<month>(?<monthnum>(0?[13578])|10)(?<sep>[-/.])))(?<day>31)(?(monthnum)|st)?)|((((?<month>(?<monthname>Jan(uary)?|Ma(r(ch)?|y)|Apr(il)?|Ju((ly?)|(ne?))|Aug(ust)?|Oct(ober)?|(Sept|Nov|Dec)(ember)?))\ )|((?<month>(?<monthnum>(0?[13-9])|1[012]))(?<sep>[-/.])))(?<day>((0?[1-9]|([12]\d)|30)|(?(monthname)(\b2?(1st|2nd|3rd|[4-9]th)|(2|3)0th|1\dth\b))))))|((((?<month>(?<monthname>Feb(ruary)?))\ )|((?<month>0?2)(?<sep>[-/.])))((?(monthname)(?<day>(\b2?(1st|2nd|3rd|[4-8]th)|9th|20th|1\dth\b)|(0?[1-9]|1\d|2[0-8])))|(?<day>29(?=(\k<sep>|(?(monthname)th)?,\ )((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00)))))))(?(sep)\k<sep>|((?(monthname)th)?,\ ))(?<year>(1[6-9]|[2-9]\d)\d{2}))$|((?<days>(31(?<suffix>st)?(?!(\ (Feb(ruary)?|Apr(il)?|June?|(Sep(?=\b|t)t?|Nov)(ember)?))|[-/.](0?[2469]|11)))|((30|29)(?<suffix>th)?(?!((\ Feb(ruary)?)|([-/.]0?2))))|(29(?<suffix>th)?(?=((\ Feb(ruary)?\ )|([ -/.]0?2))(((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00)))))|(?<suffix>(?=\d\d?[nrst][dht]\ [JFMASOND])(\b2?(1st|2nd|3rd|[4-8]th)|20th|1\dth\b)|((0?[1-9])|1\d|2[0-8])))(?<month>(\ (?<monthname>(Jan(uary)?|Feb(ruary)?|Ma(r(ch)?|y)|Apr(il)?|Ju((ly?)|(ne?))|Aug(ust)?|Oct(ober)?|(Sep(?=\b|t)t?|Nov|Dec)(ember)?))\ )|(?(\k<suffix>)|((?<sep>[-/.])(0?[1-9]|1[012])\k<sep>)))(?<year>(1[6-9]|[2-9]\d)\d{2}))|\b((?<year>((1[6-9])|([2-9]\d))\d\d)(?<sep>[/.-])(?<month>0?[1-9]|1[012])\k<sep>(?<day>((?<!(\k<sep>((0?[2469])|11)\k<sep>))31)|(?<!\k<sep>(0?2)\k<sep>)(29|30)|((?<=((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|(16|[2468][048]|[3579][26])00)\k<sep>(0?2)\k<sep>)29)|((0?[1-9])|(1\d)|(2[0-8]))))\b)(?:(?=\x20\d)\x20|$))?((?<time>((0?[1-9]|1[012])(:[0-5]\d){0,2}(\x20[AP]M))|([01]\d|2[0-3])(:[0-5]\d){1,2}))?)$");
        }

        public static bool IsBool(string target)
        {
            bool isBool;
            return Boolean.TryParse(target, out isBool);
        }
    }
}