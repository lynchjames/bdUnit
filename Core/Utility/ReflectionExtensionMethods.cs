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

        public static string GetResource(this string resourceName)
        {
            var assembly = Assembly.GetExecutingAssembly();
            var resource = assembly.GetManifestResourceStream(resourceName);
            if (resource != null)
            {
                TextReader textReader = new StreamReader(resource);
                var result = textReader.ReadToEnd();
                textReader.Close();

                return result;
            }
            return string.Empty;
        }

        public static Stream GetResourceStream(this string resourceName)
        {
            var assembly = Assembly.GetExecutingAssembly();
            var resource = assembly.GetManifestResourceStream(resourceName);
            return resource;
        }
    }
}