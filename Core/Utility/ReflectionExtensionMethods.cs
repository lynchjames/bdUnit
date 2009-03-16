#region Using Statements

using System;
using System.IO;
using System.Reflection;

#endregion

namespace bdUnit.Core.Utility
{
    public static class ReflectionExtensionMethods
    {
        public static void SetPropery(this object obj, string propertyName, object value)
        {
            var propertyInfo = obj.GetType().GetProperty(propertyName);
            if (propertyInfo == null)
            {
                throw new ArgumentException(obj.GetType() + "does not have a property " + propertyName);
            }

            propertyInfo.SetValue(obj, value, null);
        }

        public static string GetResource(string resourceName)
        {
            var assembly = Assembly.GetExecutingAssembly();
            TextReader textReader = new StreamReader(assembly.GetManifestResourceStream(resourceName));
            var result = textReader.ReadToEnd();
            textReader.Close();

            return result;
        }
    }
}