#region Using Statements

using bdUnit.Core.Enum;

#endregion

namespace bdUnit.Core.Generators
{
    public class GeneratorBase
    {
        #region TextTemplates

        public string TestFixtureText;
        public string TestText;
        public string MethodText;
        public string PropertyText;
        public string TypeText;
        public string AssertText;
        public AccessEnum Access { get; set; }

        #endregion

        protected internal static string WriteAssertMessage(string statement)
        {
            var assertBody = statement.Replace("\t", string.Empty).Replace("\n", string.Empty).Replace("\r", string.Empty).Replace("\"", @"\" + "\"");
            return string.Format("{0}, \"Failed: {1}\"", statement, assertBody);
        }
    }
}