namespace PhotoWatcher
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Text;
    using System.IO;
    using System.Windows.Media.Imaging;

    public class PhotoMetadataExtractor
    {
        BitmapMetadata mData;

        public PhotoMetadataExtractor(Stream imageStream)
        {
            JpegBitmapDecoder decoder = new JpegBitmapDecoder(
                imageStream,
                BitmapCreateOptions.None,
                BitmapCacheOption.None);

            mData = (BitmapMetadata)decoder.Frames[0].Metadata;
            
            if (mData == null)
            {
                throw new NullReferenceException("No photo metadata available!");
            }
        }

        public string Title { get { return (String.IsNullOrEmpty(mData.Title) ? "unknown" : mData.Title); } }
        public string Subject { get { return (String.IsNullOrEmpty(mData.Subject) ? "unknown" : mData.Subject); } }
        public int Rating { get { return mData.Rating; } }
        public DateTime DateTaken { get { return (mData.DateTaken == null ? DateTime.MinValue : DateTime.Parse(mData.DateTaken)); } }
        public string[] Authors
        {
            get
            {
                if (mData.Author != null)
                    return mData.Author.ToArray();
                return new string[] { "unknown" };
            }
        }
        public string Copyright { get { return (String.IsNullOrEmpty(mData.Copyright) ? "unknown" : mData.Copyright); } }
        public string CameraManufacturer { get { return (String.IsNullOrEmpty(mData.CameraManufacturer) ? "unknown" : mData.CameraManufacturer); } }
        public string CameraModel { get { return (String.IsNullOrEmpty(mData.CameraModel) ? "unknown" : mData.CameraModel); } }
    }
}
