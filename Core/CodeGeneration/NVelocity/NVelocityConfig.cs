using bdUnit.Core.Utility;
using NVelocity;
using NVelocity.App;

namespace bdUnit.Core.NVelocity
{
  public static class NVelocityConfig
  {
    private static VelocityEngine velocity;

    static NVelocityConfig()
    {
      velocity = new VelocityEngine();
      velocity.Init();
    }

    public static Template GetTemplate(TemplateEnum template)
    {
      return velocity.GetTemplate(string.Format("..//..//Templates//{0}.vm", template));
    }
  }
}