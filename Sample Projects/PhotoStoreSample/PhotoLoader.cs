namespace PhotoWatcher
{
    using System;
    using System.Diagnostics;
    using System.IO;
    using System.Text;
    using System.Text.RegularExpressions;

    public static class PhotoLoader
    {
        static string instanceDataFile = @"Gallery.input";
        static string installLocation = Path.Combine(Environment.GetEnvironmentVariable("programfiles"), 
                                                     @"Microsoft Oslo SDK 1.0");
        static string executablesPath = Path.Combine(installLocation, "Bin");
        public static string mg = Path.Combine(executablesPath, "mg.exe");
        static string mgx = Path.Combine(executablesPath, "mgx.exe");
        static string m = Path.Combine(executablesPath, "m.exe");
        static string mx = Path.Combine(executablesPath, "mx.exe");

        static string BuildInstanceDataString(PhotoMetadataExtractor extractor, string photoFileName)
        {
            string authors = (extractor.Authors == null ? string.Empty : "{{ \"" + string.Join("\",\"", extractor.Authors)) + "\" }}";
            string instanceData = String.Format(
                "PhotoInfo " +
                "\"" + extractor.Title + "\" " +
                "\"" + extractor.Subject + "\" " +
                "\"" + extractor.Rating + "\" " +
                "\"" + Path.GetFileNameWithoutExtension(photoFileName) + "\" " +
                extractor.DateTaken.ToString("yyyy-MM-dd") + " " +
                authors + " " +
                "\"" + extractor.Copyright + "\" " +
                "\"" + extractor.CameraManufacturer + "\" " +
                "\"" + extractor.CameraModel + "\" " +
                "\"" + Path.GetFullPath(photoFileName) + "\" "
                );
            return instanceData;
        }

        public static void ExecuteProgram(string exe, params string[] args)
        {
            StringBuilder sb = new StringBuilder();
            foreach (string arg in args)
            {
                sb.AppendFormat("{0} ", arg);
            }
            ProcessStartInfo info = new ProcessStartInfo(exe, sb.ToString());
            info.RedirectStandardOutput = true;
            info.RedirectStandardError = true;
            info.UseShellExecute = false;
            info.CreateNoWindow = true;

            Process p = Process.Start(info);
            StringWriter errorBuffer = new StringWriter();
            StringWriter outputBuffer = new StringWriter();
            p.ErrorDataReceived += (o, e) => errorBuffer.WriteLine(e.Data);
            p.OutputDataReceived += (o, e) => outputBuffer.WriteLine(e.Data);
            p.BeginOutputReadLine();
            p.BeginErrorReadLine();
            p.WaitForExit();
            string error = errorBuffer.ToString();
            string output = outputBuffer.ToString();
        }

        public static void LoadPhoto(string photoFileName)
        {
            ReadAndSavePhotoMetadata(photoFileName);
            RunMToolChain();
        }

        static void ReadAndSavePhotoMetadata(string photoFileName)
        {
            try
            {
                Stream imageStream = new FileStream(
                    photoFileName, 
                    FileMode.Open, 
                    FileAccess.ReadWrite, 
                    FileShare.ReadWrite);

                Console.WriteLine(String.Format("Found new file: {0}", Path.GetFileName(photoFileName)));

                PhotoMetadataExtractor extractor = new PhotoMetadataExtractor(imageStream);

                // save instance data file
                using (StreamWriter sw = new StreamWriter(instanceDataFile))
                {
                    sw.WriteLine(BuildInstanceDataString(extractor, photoFileName));
                }
                Console.WriteLine(String.Format("Instance data saved to {0}\n", instanceDataFile));
            }
            catch (FileNotFoundException)
            {
                Console.WriteLine(String.Format("Cannot read {0}. Skipping.", photoFileName));
                return;
            }          
        }

        static void RunMToolChain()
        {
            Console.WriteLine("Compiling photo data file with M grammar into M instance data file...", 1);
            ExecuteProgram(mgx, @"/r:Gallery.mgx", instanceDataFile);
            if (!File.Exists(@"Gallery.m"))
            {
                Console.WriteLine("Compiling input file failed. Skipping.", 1);
                return;
            }
            Console.WriteLine("M instance data file created OK\n", 1);

            // Fix the .m file (M compiler is not fully compatible with M grammar )
            using (StreamReader reader = new StreamReader("Gallery.m"))
            {
                string content = reader.ReadToEnd();

                content = Regex.Replace(content, @"FullPath {", @"FullPath = {" );
                content = Regex.Replace(content, @"Authors {", @"Authors = {" );
                content = content.Replace("\\", "\\\\");
                using (StreamWriter writer = new StreamWriter("GalleryProper.m"))                
                {
                    writer.Write(content);
                }
            }

            Console.WriteLine("Compiling M instance data file into image...", 1);
            ExecuteProgram(m, @"/t:Repository /p:Image /r:Photo.mx /o:Gallery.mx", @"galleryproper.m");
            if (!File.Exists(@"Gallery.mx"))
            {
                Console.WriteLine("Compiling m file failed. Skipping.", 1);
                return;
            }
            Console.WriteLine("Image created OK\n", 1);

            Console.WriteLine("Loading instance data into Repository...", 1);
            ExecuteProgram(mx, @"/i:Gallery.mx /ig /s:. /db:Repository");
            Console.WriteLine("Instance data loaded into Repository OK", 1);
            
            Console.WriteLine("Yay!" + Environment.NewLine);
            Console.WriteLine("--------------------------------------------", 1);
            Console.WriteLine("Waiting for another photo...");
            Console.WriteLine("\nType <Ctrl>+C to stop monitor.\n");
        }
    }
}
