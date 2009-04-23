#region Using Statements

using System.Collections.Generic;
using bdUnit.Core.AST;
using bdUnit.Core.Templates;
using NVelocity;

#endregion

namespace bdUnit.Core.Extensions
{
    public static class NVelocityCodeGenerationExtensions
    {
        public static string AsNVelocityTemplate(this ConcreteClass @class, TemplateEnum template)
        {
            var context = new VelocityContext();
            context.Put("concreteClass", @class);
            return NVelocityConfig.MergeTemplate(context, template);
        }

        public static string AsNVelocityTemplate(this TargetProperty property, TemplateEnum template)
        {
            var context = new VelocityContext();
            context.Put("property", property);
            return NVelocityConfig.MergeTemplate(context, template);
        }

        public static string AsNVelocityTemplate(this Dictionary<string, object> inputs, TemplateEnum template)
        {
            var context = new VelocityContext();
            foreach (var input in inputs)
            {
                context.Put(input.Key, input.Value);
            }
            return NVelocityConfig.MergeTemplate(context, template);
        }

        public static string AsNVelocityTemplate(this string text, string placeHolderName, TemplateEnum template)
        {
            var context = new VelocityContext();
            context.Put(placeHolderName, text);
            return NVelocityConfig.MergeTemplate(context, template);
        }

        public static string GetNVelocityTemplate(TemplateEnum template)
        {
            var context = new VelocityContext();
            return NVelocityConfig.MergeTemplate(context, template);
        }
    }
}