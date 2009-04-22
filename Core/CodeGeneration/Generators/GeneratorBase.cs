#region Using Statements

using bdUnit.Core.Enum;

#endregion

namespace bdUnit.Core.Generators
{
    public class GeneratorBase
    {
        #region TextTemplates

        public string AssertText;
        public string MethodText;
        public string PropertyText;
        public string TestFixtureText;
        public string TestText;
        public string TypeText;
        public AccessEnum Access { get; set; }

        #endregion

        public static string WriteAssertMessage(string statement)
        {
            var assertBody =
                statement.Replace("\t", string.Empty).Replace("\n", string.Empty).Replace("\r", string.Empty).Replace(
                    "\"", @"\" + "\"");
            return string.Format("{0}, \"Failed: {1}\"", statement, assertBody);
        }
    }
}