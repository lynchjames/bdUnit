#region Using Statements

using System.ComponentModel;

#endregion

namespace bdUnit.Preview
{
    public class BackgroundThread : BackgroundWorker
    {
        public BackgroundThread()
        {
            WorkerReportsProgress = true;
            WorkerSupportsCancellation = true;
        }

        public void Generate()
        {
            RunWorkerAsync();
        }
    }
}
