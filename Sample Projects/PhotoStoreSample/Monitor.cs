namespace PhotoWatcher
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Text;
    using System.IO;
    using System.Threading;

    class Monitor
    {
        static void Main(string[] args)
        {
            // compile grammar
            Console.WriteLine("--------------------------------------------", 1);
            Console.WriteLine("Compiling grammar...", 1);
            PhotoLoader.ExecuteProgram(PhotoLoader.mg, @"/t:Mgx", @"Gallery.mg");
            
            if (!File.Exists(@"Gallery.mgx"))
            {
                Console.WriteLine("Compiling grammar file failed. Exiting...", 1);
                return;
            }
            Console.WriteLine("Grammar OK\n", 1);

            Monitor monitor = new Monitor();
            Console.WriteLine("--------------------------------------------", 1);
            Console.WriteLine("Starting monitor...");
            monitor.StartMonitor();
            Console.WriteLine("Monitor started OK\n");
            Console.WriteLine("\nType <Ctrl>+C to stop monitor.\n");

            while (true)
            {
            }
        }

        public void StartMonitor()
        {
            FileSystemWatcher watcher;
            watcher = new FileSystemWatcher(Environment.CurrentDirectory, "*.jpg");
            watcher.Created += new FileSystemEventHandler(OnPhotoAdded);
            watcher.EnableRaisingEvents = true;
        }

        public void OnPhotoAdded(object source, FileSystemEventArgs e)
        {
            //Console.WriteLine(e.FullPath);
            Thread.Sleep(1000);
            PhotoLoader.LoadPhoto(e.FullPath);
        }
    }
}