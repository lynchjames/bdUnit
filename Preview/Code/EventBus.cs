#region Using Statements

using System;

#endregion

namespace bdUnit.Preview.Code
{
    public class EventBus
    {
        public static EventHandler AppExit;
        public static EventHandler FrameworkChecked;
        public static EventHandler TextChanged;
        public static EventHandler TextSaved;

        public static void OnFrameworkChecked(object sender, EventArgs e)
        {
            if (FrameworkChecked != null)
            {
                FrameworkChecked(sender, e);
            }
        }

        public static void OnTextChanged(object sender, TargetEventArgs e)
        {
            if (TextChanged != null)
            {
                TextChanged(sender, e);
            }
        }

        public static void OnTextSaved(object sender, TargetEventArgs e)
        {
            if (TextSaved != null)
            {
                TextSaved(sender, e);
            }
        }

        public static void OnAppExit(object sender, EventArgs e)
        {
            if (AppExit != null)
            {
                AppExit(sender, e);
            }
        }
    }
}