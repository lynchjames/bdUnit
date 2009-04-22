#region Using Statements

using System.Collections.Generic;
using NVelocity;
using NVelocity.App;
using bdUnit.Core.Utility;

#endregion

namespace bdUnit.Core.Templates
{
  public static class NVelocityConfig
  {
    private static VelocityEngine velocity;

    static NVelocityConfig()
    {
      velocity = new VelocityEngine();
      velocity.AddProperty("assembly.resource.loader.assembly", new[] { "bdUnit.Core" });
      velocity.Init();
    }

    public static Template GetTemplate(TemplateEnum template)
    {
        var templateResource = template.ToString().GetResource();
        return velocity.GetTemplate(string.Format("bdUnit.Core.CodeGeneration.NVelocity.Templates.{0}.vm", template));
    }
  }
}