using NVelocity;
using NVelocity.App;

namespace bdUnit.Core.NVelocity
{
  public static class NVelocityInitializer
  {
    private static VelocityEngine velocity;

    static NVelocityInitializer()
    {
      velocity = new VelocityEngine();
      velocity.Init();
    }

    public static Template GetTemplate(TemplateEnum template)
    {
      return velocity.GetTemplate(string.Format("/Templates?{0}.vm", template));
    }
  }
}