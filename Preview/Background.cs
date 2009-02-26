using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.ComponentModel;

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
