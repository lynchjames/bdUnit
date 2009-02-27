using System;
using System.Collections.Generic;
using System.Text;
using System.Windows;
using System.Windows.Media;
using System.Windows.Markup;
using System.Xml;
using System.IO;
using System.ComponentModel;
using System.Windows.Controls;

namespace Wpf.Controls
{
    class Helper
    {        
        /// <summary>
        /// Find a specific parent object type in the visual tree
        /// </summary>
        public static T FindParentControl<T>(DependencyObject outerDepObj) where T : DependencyObject
        {
            DependencyObject dObj = VisualTreeHelper.GetParent(outerDepObj);
            if (dObj == null)
                return null;

            if (dObj is T)
                return dObj as T;

            while ((dObj = VisualTreeHelper.GetParent(dObj)) != null)
            {
                if (dObj is T)
                    return dObj as T;
            }
            
            return null;
        }

        /// <summary>
        /// Find the Panel for the TabControl
        /// </summary>
        public static VirtualizingTabPanel FindVirtualizingTabPanel(Visual visual)
        {
            if (visual == null)
                return null;

            for (int i = 0; i < VisualTreeHelper.GetChildrenCount(visual); i++)
            {
                Visual child = VisualTreeHelper.GetChild(visual, i) as Visual;

                if (child != null)
                {
                    if (child is VirtualizingTabPanel)
                    {
                        object temp = child;
                        return (VirtualizingTabPanel)temp;
                    }

                    VirtualizingTabPanel panel = FindVirtualizingTabPanel(child);
                    if (panel != null)
                    {
                        object temp = panel;
                        return (VirtualizingTabPanel)temp; // return the panel up the call stack
                    }
                }
            }
            return null;
        }

        /// <summary>
        /// Clone an element
        /// </summary>
        /// <param name="elementToClone"></param>
        /// <returns></returns>
        public static object CloneElement(object elementToClone)
        {
            string xaml = XamlWriter.Save(elementToClone);
            return XamlReader.Load(new XmlTextReader(new StringReader(xaml)));
        }

    }
}
