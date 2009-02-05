using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace WinGallery
{
    public partial class GalleryForm : Form
    {
        public GalleryForm()
        {
            InitializeComponent();
        }

        private void GalleryForm_Load(object sender, EventArgs e)
        {
            this.galleryTableAdapter.Fill(this.repositoryDataSet.Gallery);
        }
    }
}
