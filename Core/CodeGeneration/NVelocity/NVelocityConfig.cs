#region Using Statements

using System.IO;
using NVelocity;
using NVelocity.App;
using NVelocity.Context;

#endregion

namespace bdUnit.Core.Templates
{
    public static class NVelocityConfig
    {
        private static readonly string[] TemplateResourceLocations = {
                                                                         "Templates", "Templates.NUnit", "Templates.XUnit",
                                                                         "Templates.MbUnit", "Templates.StructureMap", "Templates.Input"
                                                                     };
        private static readonly VelocityEngine velocity;

        static NVelocityConfig()
        {
            velocity = new VelocityEngine();
            velocity.AddProperty("assembly.resource.loader.assembly", new[] {"bdUnit.Core"});
            velocity.Init();
        }

        public static Template GetTemplate(TemplateEnum template)
        {
            var count = TemplateResourceLocations.Length;
            for (var i = 0; i < count; i++)
            {
                var folder = TemplateResourceLocations[i];
                var location = string.Format("bdUnit.Core.CodeGeneration.NVelocity.{0}.{1}.vm", folder, template);
                if (velocity.TemplateExists(location))
                {
                    return velocity.GetTemplate(location);
                }
            }
            return null;
        }

        public static string MergeTemplate(IContext context, TemplateEnum templateName)
        {
            var writer = new StringWriter();
            var template = GetTemplate(templateName);
            template.Merge(context, writer);
            return writer.GetStringBuilder().ToString();
        }
    }
}