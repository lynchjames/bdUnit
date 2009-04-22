using System.IO;
using bdUnit.Core.AST;
using bdUnit.Core.Templates;
using NVelocity;

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

    public static string ToTemplatedString(this VelocityContext context, TemplateEnum templateName)
    {
      var writer = new StringWriter();
      var template = NVelocityConfig.GetTemplate(templateName);
      template.Merge(context, writer);
      return writer.GetStringBuilder().ToString();
    }
  }
}