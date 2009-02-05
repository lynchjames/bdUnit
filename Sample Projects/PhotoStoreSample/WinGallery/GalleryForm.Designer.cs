namespace WinGallery
{
    partial class GalleryForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.repositoryDataSet = new WinGallery.RepositoryDataSet();
            this.galleryBindingSource = new System.Windows.Forms.BindingSource(this.components);
            this.galleryTableAdapter = new WinGallery.RepositoryDataSetTableAdapters.GalleryTableAdapter();
            this.nameDataGridViewTextBoxColumn = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.titleDataGridViewTextBoxColumn = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.subjectDataGridViewTextBoxColumn = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ratingDataGridViewTextBoxColumn = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dateTakenDataGridViewTextBoxColumn = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.copyrightDataGridViewTextBoxColumn = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.cameraManufacturerDataGridViewTextBoxColumn = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.cameraModelDataGridViewTextBoxColumn = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.fullPathDataGridViewTextBoxColumn = new System.Windows.Forms.DataGridViewTextBoxColumn();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryDataSet)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.galleryBindingSource)).BeginInit();
            this.SuspendLayout();
            // 
            // dataGridView1
            // 
            this.dataGridView1.AllowUserToAddRows = false;
            this.dataGridView1.AllowUserToDeleteRows = false;
            this.dataGridView1.AllowUserToOrderColumns = true;
            this.dataGridView1.AutoGenerateColumns = false;
            this.dataGridView1.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.AllCells;
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.nameDataGridViewTextBoxColumn,
            this.titleDataGridViewTextBoxColumn,
            this.subjectDataGridViewTextBoxColumn,
            this.ratingDataGridViewTextBoxColumn,
            this.dateTakenDataGridViewTextBoxColumn,
            this.copyrightDataGridViewTextBoxColumn,
            this.cameraManufacturerDataGridViewTextBoxColumn,
            this.cameraModelDataGridViewTextBoxColumn,
            this.fullPathDataGridViewTextBoxColumn});
            this.dataGridView1.DataSource = this.galleryBindingSource;
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.ReadOnly = true;
            this.dataGridView1.Size = new System.Drawing.Size(292, 273);
            this.dataGridView1.TabIndex = 0;
            // 
            // repositoryDataSet
            // 
            this.repositoryDataSet.DataSetName = "RepositoryDataSet";
            this.repositoryDataSet.SchemaSerializationMode = System.Data.SchemaSerializationMode.IncludeSchema;
            // 
            // galleryBindingSource
            // 
            this.galleryBindingSource.DataMember = "Gallery";
            this.galleryBindingSource.DataSource = this.repositoryDataSet;
            // 
            // galleryTableAdapter
            // 
            this.galleryTableAdapter.ClearBeforeFill = true;
            // 
            // nameDataGridViewTextBoxColumn
            // 
            this.nameDataGridViewTextBoxColumn.DataPropertyName = "Name";
            this.nameDataGridViewTextBoxColumn.HeaderText = "Name";
            this.nameDataGridViewTextBoxColumn.Name = "nameDataGridViewTextBoxColumn";
            this.nameDataGridViewTextBoxColumn.ReadOnly = true;
            this.nameDataGridViewTextBoxColumn.Width = 60;
            // 
            // titleDataGridViewTextBoxColumn
            // 
            this.titleDataGridViewTextBoxColumn.DataPropertyName = "Title";
            this.titleDataGridViewTextBoxColumn.HeaderText = "Title";
            this.titleDataGridViewTextBoxColumn.Name = "titleDataGridViewTextBoxColumn";
            this.titleDataGridViewTextBoxColumn.ReadOnly = true;
            this.titleDataGridViewTextBoxColumn.Width = 52;
            // 
            // subjectDataGridViewTextBoxColumn
            // 
            this.subjectDataGridViewTextBoxColumn.DataPropertyName = "Subject";
            this.subjectDataGridViewTextBoxColumn.HeaderText = "Subject";
            this.subjectDataGridViewTextBoxColumn.Name = "subjectDataGridViewTextBoxColumn";
            this.subjectDataGridViewTextBoxColumn.ReadOnly = true;
            this.subjectDataGridViewTextBoxColumn.Width = 68;
            // 
            // ratingDataGridViewTextBoxColumn
            // 
            this.ratingDataGridViewTextBoxColumn.DataPropertyName = "Rating";
            this.ratingDataGridViewTextBoxColumn.HeaderText = "Rating";
            this.ratingDataGridViewTextBoxColumn.Name = "ratingDataGridViewTextBoxColumn";
            this.ratingDataGridViewTextBoxColumn.ReadOnly = true;
            this.ratingDataGridViewTextBoxColumn.Width = 63;
            // 
            // dateTakenDataGridViewTextBoxColumn
            // 
            this.dateTakenDataGridViewTextBoxColumn.DataPropertyName = "Date Taken";
            this.dateTakenDataGridViewTextBoxColumn.HeaderText = "Date Taken";
            this.dateTakenDataGridViewTextBoxColumn.Name = "dateTakenDataGridViewTextBoxColumn";
            this.dateTakenDataGridViewTextBoxColumn.ReadOnly = true;
            this.dateTakenDataGridViewTextBoxColumn.Width = 82;
            // 
            // copyrightDataGridViewTextBoxColumn
            // 
            this.copyrightDataGridViewTextBoxColumn.DataPropertyName = "Copyright";
            this.copyrightDataGridViewTextBoxColumn.HeaderText = "Copyright";
            this.copyrightDataGridViewTextBoxColumn.Name = "copyrightDataGridViewTextBoxColumn";
            this.copyrightDataGridViewTextBoxColumn.ReadOnly = true;
            this.copyrightDataGridViewTextBoxColumn.Width = 76;
            // 
            // cameraManufacturerDataGridViewTextBoxColumn
            // 
            this.cameraManufacturerDataGridViewTextBoxColumn.DataPropertyName = "Camera Manufacturer";
            this.cameraManufacturerDataGridViewTextBoxColumn.HeaderText = "Camera Manufacturer";
            this.cameraManufacturerDataGridViewTextBoxColumn.Name = "cameraManufacturerDataGridViewTextBoxColumn";
            this.cameraManufacturerDataGridViewTextBoxColumn.ReadOnly = true;
            this.cameraManufacturerDataGridViewTextBoxColumn.Width = 123;
            // 
            // cameraModelDataGridViewTextBoxColumn
            // 
            this.cameraModelDataGridViewTextBoxColumn.DataPropertyName = "Camera Model";
            this.cameraModelDataGridViewTextBoxColumn.HeaderText = "Camera Model";
            this.cameraModelDataGridViewTextBoxColumn.Name = "cameraModelDataGridViewTextBoxColumn";
            this.cameraModelDataGridViewTextBoxColumn.ReadOnly = true;
            this.cameraModelDataGridViewTextBoxColumn.Width = 92;
            // 
            // fullPathDataGridViewTextBoxColumn
            // 
            this.fullPathDataGridViewTextBoxColumn.DataPropertyName = "Full Path";
            this.fullPathDataGridViewTextBoxColumn.HeaderText = "Full Path";
            this.fullPathDataGridViewTextBoxColumn.Name = "fullPathDataGridViewTextBoxColumn";
            this.fullPathDataGridViewTextBoxColumn.ReadOnly = true;
            this.fullPathDataGridViewTextBoxColumn.Width = 68;
            // 
            // GalleryForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(292, 273);
            this.Controls.Add(this.dataGridView1);
            this.Name = "GalleryForm";
            this.Text = "Gallery";
            this.Load += new System.EventHandler(this.GalleryForm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.repositoryDataSet)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.galleryBindingSource)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.DataGridView dataGridView1;
        private RepositoryDataSet repositoryDataSet;
        private System.Windows.Forms.BindingSource galleryBindingSource;
        private WinGallery.RepositoryDataSetTableAdapters.GalleryTableAdapter galleryTableAdapter;
        private System.Windows.Forms.DataGridViewTextBoxColumn nameDataGridViewTextBoxColumn;
        private System.Windows.Forms.DataGridViewTextBoxColumn titleDataGridViewTextBoxColumn;
        private System.Windows.Forms.DataGridViewTextBoxColumn subjectDataGridViewTextBoxColumn;
        private System.Windows.Forms.DataGridViewTextBoxColumn ratingDataGridViewTextBoxColumn;
        private System.Windows.Forms.DataGridViewTextBoxColumn dateTakenDataGridViewTextBoxColumn;
        private System.Windows.Forms.DataGridViewTextBoxColumn copyrightDataGridViewTextBoxColumn;
        private System.Windows.Forms.DataGridViewTextBoxColumn cameraManufacturerDataGridViewTextBoxColumn;
        private System.Windows.Forms.DataGridViewTextBoxColumn cameraModelDataGridViewTextBoxColumn;
        private System.Windows.Forms.DataGridViewTextBoxColumn fullPathDataGridViewTextBoxColumn;
    }
}

