use Repository
go

create view [Gallery].[Gallery] as
select [Gallery].[Photos].Name, [Gallery].[Photos].Title, [Gallery].[Photos].Subject, [Gallery].[Photos].Rating, [Gallery].[Photos].DateTaken as [Date Taken],
	   [Gallery].[Photos].Copyright, [Gallery].[Photos].CameraManufacturer as [Camera Manufacturer], [Gallery].[Photos].CameraModel as [Camera Model],
	   [Gallery].[FullSizePhotos].FullPath as [Full Path]
from Gallery.Photos 
left outer join Gallery.FullSizePhotos on Gallery.Photos.FullPath = Gallery.FullSizePhotos.Id     
go

grant select on object::[Gallery].[Gallery] to [RepositoryReader];
go