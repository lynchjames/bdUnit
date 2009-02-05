#region Using Statements

using System;

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
    }
}