module Gallery
{
    language PhotoLanguage 
    {
        interleave Skippable 
            = Whitespace;
         
        syntax Main 
            = photos:Photo+ 
            => Photos{ valuesof(photos) };
         
        syntax Photo 
            = PhotoStart title:Title subject:Subject rating:Rating 
            filename:FileName thumbnailpath:ThumbnailPath dateTaken:DateTaken OpenBrace authors:AuthorName+ ClosedBrace 
            copyright:CopyRight manufacturer:CameraManufacturer model:CameraModel fullPath:FullPath
            => { Title{title}, Subject{subject}, Rating{rating}, ThumbnailPath{thumbnailpath}, Name {filename}, DateTaken {dateTaken}, Authors {valuesof(authors)}, Copyright {copyright},
              CameraManufacturer{manufacturer}, CameraModel{model}, FullPath{fullPath}} 
           | PhotoStart title:Title subject:Subject rating:Rating filename:FileName thumbnailpath:ThumbnailPath dateTaken:DateTaken copyright:CopyRight 
              manufacturer:CameraManufacturer model:CameraModel fullPath:FullPath 
            => { Title{title}, Subject{subject}, Rating{rating}, Name {filename}, ThumbnailPath{thumbnailpath}, DateTaken {dateTaken}, Copyright {copyright},
              CameraManufacturer{manufacturer}, CameraModel{model}, FullPath{fullPath}};
        
        syntax Authors
            = OpenBrace name:AuthorName ClosedBrace => name
            | OpenBrace name:AuthorName ',' names:AuthorName+ ClosedBrace => {name, valuesof(names)}
            ;
            
        syntax AuthorName 
            = name:Name => 
             Name {name}
            | name:Name => 
             Name {name}
            | name:Name',' => {Name {name}}
            | name:NameVerbatim => {Name {name}}
            | name:NameVerbatim',' => {Name {name}};
            //| name:AuthorName names:AuthorName+ =>{Name{name}, valuesof(names)} ;
            
        syntax Title 
            = name:Name => name
            | name: NameVerbatim => name;
            
        syntax Subject
            = name:Name => name
            | name: NameVerbatim => name;
            
        syntax Rating
            = rating:RatingValue => rating
            | rating:NameVerbatim => rating;       
            
            
        syntax FileName    
            = name:Name => name
            | name: NameVerbatim => name;
            
        syntax ThumbnailPath
            = name:Name => name
            | name: NameVerbatim => name; 
                
        syntax FileType
            = name:Name => name
            | name: NameVerbatim => name;

        syntax FullPath
            = name:Name => FullPath{name}
            | name: NameVerbatim => FullPath{name};

        syntax FileFormat    
            = name:Name => name
            | name: NameVerbatim => name;
            
            
        syntax DateTaken   
            = name:DateValue => name
            | name: DateValue => name;
            
        syntax CopyRight   
            = name:Name => name
            | name: NameVerbatim => name;

        syntax CameraManufacturer   
            = name:Name => name
            | name: NameVerbatim => name;
            
       syntax CameraModel   
            = name:Name => name
            | name: NameVerbatim => name;
           
        nest syntax NameVerbatim 
            = '"' name:NameWithWhitespace '"' => name;

        syntax NumberVerbatim 
            = '"' name:RatingValue '"' => name;


        token AlphaNumerical 
            = 'a'..'z' | 'A'..'Z' | '0'..'9' | '.' | ':' | '\\' | '(' | ')' | '/';

        token Numerical
            = '0'..'9';

        final token PhotoStart 
            = "PhotoInfo";
         
        token Name 
            = AlphaNumerical+;
        
        token NameWithWhitespace 
            = (AlphaNumerical | Whitespace)+;
            
        token RatingValue
             = Numerical#1..9;
             
        token DateValue
            = Numerical#4'-'Numerical#2'-'Numerical#2;
                 
        token Whitespace
            = '\r' 
            | '\n' 
            | '\t' 
            | ' ';
        
        token OpenBrace
           = '{';
           
        token ClosedBrace
           = '}';   
           
    }
}