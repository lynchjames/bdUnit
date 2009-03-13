namespace bdUnit.Core
{
    public class Settings
    {
        private static string _grammarPath = "/Development/bdUnit/bdUnit/Core/Grammar/TestWrapper.mg";
        
        public static string GrammarPath
        {
            get { return _grammarPath ; }
            set { _grammarPath = value; }
        }
    }
}
