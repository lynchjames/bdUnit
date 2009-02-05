module Gallery
{
    Photos : Photo* where item.FullPath in FullSizePhotos, item.Authors <= Photographers;
    
    type Photo
    {
        Id : Integer64 = AutoNumber();
        
        Folder : Integer32 = 1;
        
        // Description
        Title : Text;
        
        Subject : Text;
        
        Rating : Text;
        
        // File
        Name : Text;
        
        // Origin
        DateTaken : Text;
        
        Authors : Photographers*;
        
        Copyright : Text;
        
        // Camera        
        CameraManufacturer : Text;
        
        CameraModel : Text;       
        
        FullPath : FullSizePhoto;        
        
    } where identity Id;
    
    Photographers : Photographer*;
    
    type Photographer
    {
        Id : Integer64 = AutoNumber();
        
        Folder : Integer32 = 1;

        Name : Text;
    
    } where identity Id;   
    
    
    FullSizePhotos : FullSizePhoto*;
    
    type FullSizePhoto
    {
        Id : Integer64 = AutoNumber();       
        
        Folder : Integer32 = 100;
		
        FullPath : Text;
	
    } where identity Id;
    
}