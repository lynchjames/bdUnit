#region Using Statements

using System.Text;
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

        protected static void WriteToTrace(StringBuilder text, string statement)
        {
            statement = statement.Replace("\t", string.Empty).Replace("\n", string.Empty).Replace("\r", string.Empty).Replace("\"", @"\" + "\"");
            text.AppendLine(string.Format("\t\t\tDebug.WriteLine(\"{0}\");", statement));
            return;
        }
    }
}