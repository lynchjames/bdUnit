#region Using Statements

using System.Collections.Generic;
using System.IO;
using bdUnit.Core.AST;
using bdUnit.Core.Templates;
using NVelocity;
using NVelocity.Context;

#endregion

namespace bdUnit.Core.Extensions
{
    public static class NVelocityCodeGenerationExtensions
    {
        public static string AsNVelocityTemplate(this ConcreteClass @class, TemplateEnum template)
        {
            var context = new VelocityContext();
            context.Put("concreteClass", @class);
            return context.ToTemplatedString(template);
        }

        public static string AsNVelocityTemplate(this TargetProperty property, TemplateEnum template)
        {
            var context = new VelocityContext();
            context.Put("property", property);
            return context.ToTemplatedString(template);
        }

        public static string AsNVelocityTemplate(this Dictionary<string, object> inputs, TemplateEnum template)
        {
            var context = new VelocityContext();
            foreach (var input in inputs)
            {
                context.Put(input.Key, input.Value);
            }
            return context.ToTemplatedString(template);
        }

        private static string ToTemplatedString(this IContext context, TemplateEnum templateName)
        {
            var writer = new StringWriter();
            var template = NVelocityConfig.GetTemplate(templateName);
            template.Merge(context, writer);
            return writer.GetStringBuilder().ToString();
        }
    }
}